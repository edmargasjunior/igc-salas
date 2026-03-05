"""
Processador de importação CSV para planejamento semestral.
Valida, detecta conflitos e importa reservas em lote.
"""
import csv
import io
import logging
from datetime import datetime, date, time
from django.utils import timezone

logger = logging.getLogger('apps.importacao')

# Cabeçalhos esperados no CSV (case-insensitive)
CABECALHOS_OBRIGATORIOS = [
    'codigo_sala', 'data', 'hora_inicio', 'hora_fim', 'disciplina_codigo', 'turma_codigo'
]
CABECALHOS_OPCIONAIS = ['motivo', 'professor_siape', 'recorrente', 'dia_semana', 'data_fim']


class ProcessadorCSV:
    """Processa e valida arquivo CSV de planejamento semestral."""

    def __init__(self, usuario):
        self.usuario = usuario
        self.erros = []
        self.avisos = []
        self.linhas_validas = []
        self.conflitos = []

    def processar(self, conteudo_arquivo):
        """
        Lê, valida e verifica conflitos no CSV.
        Retorna relatório sem salvar no banco.
        """
        linhas = self._ler_csv(conteudo_arquivo)
        if self.erros:
            return self._relatorio()

        for i, linha in enumerate(linhas, start=2):
            resultado = self._validar_linha(i, linha)
            if resultado:
                conflito = self._verificar_conflito_linha(resultado)
                if conflito:
                    self.conflitos.append({
                        'linha': i,
                        'dados': resultado,
                        'conflito_com': conflito
                    })
                else:
                    self.linhas_validas.append({'linha': i, 'dados': resultado})

        return self._relatorio()

    def importar(self, conteudo_arquivo):
        """Importa efetivamente as reservas válidas após validação."""
        from apps.reservas.models import Reserva, LogReserva
        from apps.estrutura.models import Sala
        from apps.academico.models import Disciplina, Turma

        self.processar(conteudo_arquivo)
        importadas = 0
        erros_importacao = []

        for item in self.linhas_validas:
            try:
                dados = item['dados']
                sala = Sala.objects.get(codigo=dados['codigo_sala'], ativo=True)

                # Buscar turma
                turma = None
                try:
                    disc = Disciplina.objects.get(codigo=dados['disciplina_codigo'])
                    turma = Turma.objects.filter(
                        disciplina=disc,
                        codigo=dados['turma_codigo'],
                        ativo=True
                    ).order_by('-ano').first()
                except (Disciplina.DoesNotExist, Turma.DoesNotExist):
                    pass

                reserva = Reserva.objects.create(
                    sala=sala,
                    solicitante=self.usuario,
                    turma=turma,
                    tipo=Reserva.Tipo.RECORRENTE if dados.get('recorrente') == 'sim' else Reserva.Tipo.PONTUAL,
                    data_inicio=dados['data_obj'],
                    data_fim=dados.get('data_fim_obj'),
                    hora_inicio=dados['hora_inicio_obj'],
                    hora_fim=dados['hora_fim_obj'],
                    motivo=dados.get('motivo', f"Importado via CSV — {dados['disciplina_codigo']}"),
                    status=Reserva.Status.APROVADA,
                    aprovado_por=self.usuario,
                    data_aprovacao=timezone.now(),
                )
                LogReserva.objects.create(
                    reserva=reserva,
                    usuario=self.usuario,
                    acao=LogReserva.Acao.CRIADA,
                    descricao=f"Importado via CSV (linha {item['linha']})"
                )
                importadas += 1
            except Exception as e:
                erros_importacao.append(f"Linha {item['linha']}: {str(e)}")
                logger.error(f"Erro ao importar linha {item['linha']}: {e}")

        return {
            'importadas': importadas,
            'erros_importacao': erros_importacao,
            'conflitos_ignorados': len(self.conflitos),
            'total_erros': len(self.erros),
        }

    def _ler_csv(self, conteudo):
        """Lê e valida estrutura do CSV."""
        try:
            if isinstance(conteudo, bytes):
                conteudo = conteudo.decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(conteudo))
            cabecalhos = [h.strip().lower().replace(' ', '_') for h in (reader.fieldnames or [])]

            faltando = [c for c in CABECALHOS_OBRIGATORIOS if c not in cabecalhos]
            if faltando:
                self.erros.append(f"Colunas obrigatórias ausentes: {', '.join(faltando)}")
                return []

            linhas = []
            for row in reader:
                linha_norm = {k.strip().lower().replace(' ', '_'): v.strip() for k, v in row.items()}
                linhas.append(linha_norm)
            return linhas
        except Exception as e:
            self.erros.append(f"Erro ao ler CSV: {str(e)}")
            return []

    def _validar_linha(self, num, linha):
        """Valida e converte uma linha do CSV."""
        erros_linha = []

        # Sala
        codigo_sala = linha.get('codigo_sala', '').strip()
        if not codigo_sala:
            erros_linha.append("codigo_sala vazio")

        # Data
        data_str = linha.get('data', '').strip()
        data_obj = None
        try:
            data_obj = datetime.strptime(data_str, '%d/%m/%Y').date()
        except ValueError:
            try:
                data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                erros_linha.append(f"data inválida '{data_str}' (use dd/mm/aaaa)")

        # Horários
        hora_inicio_obj = self._parse_hora(linha.get('hora_inicio', ''))
        hora_fim_obj = self._parse_hora(linha.get('hora_fim', ''))
        if not hora_inicio_obj:
            erros_linha.append(f"hora_inicio inválida '{linha.get('hora_inicio')}'")
        if not hora_fim_obj:
            erros_linha.append(f"hora_fim inválida '{linha.get('hora_fim')}'")
        if hora_inicio_obj and hora_fim_obj and hora_fim_obj <= hora_inicio_obj:
            erros_linha.append("hora_fim deve ser posterior à hora_inicio")

        # Disciplina e Turma
        if not linha.get('disciplina_codigo'):
            erros_linha.append("disciplina_codigo vazio")
        if not linha.get('turma_codigo'):
            erros_linha.append("turma_codigo vazio")

        if erros_linha:
            self.erros.append({'linha': num, 'erros': erros_linha})
            return None

        # Data fim (recorrência)
        data_fim_obj = None
        if linha.get('data_fim'):
            try:
                data_fim_obj = datetime.strptime(linha['data_fim'], '%d/%m/%Y').date()
            except ValueError:
                try:
                    data_fim_obj = datetime.strptime(linha['data_fim'], '%Y-%m-%d').date()
                except ValueError:
                    self.avisos.append(f"Linha {num}: data_fim inválida, ignorada")

        return {
            'codigo_sala': codigo_sala,
            'data_obj': data_obj,
            'hora_inicio_obj': hora_inicio_obj,
            'hora_fim_obj': hora_fim_obj,
            'data_fim_obj': data_fim_obj,
            'disciplina_codigo': linha.get('disciplina_codigo', ''),
            'turma_codigo': linha.get('turma_codigo', ''),
            'motivo': linha.get('motivo', ''),
            'recorrente': linha.get('recorrente', 'nao').lower(),
            'raw': linha,
        }

    def _verificar_conflito_linha(self, dados):
        """Verifica se já existe reserva aprovada no mesmo horário e sala."""
        from apps.reservas.models import Reserva
        from apps.estrutura.models import Sala
        from django.db.models import Q

        try:
            sala = Sala.objects.get(codigo=dados['codigo_sala'], ativo=True)
        except Sala.DoesNotExist:
            self.erros.append({'linha': '?', 'erros': [f"Sala '{dados['codigo_sala']}' não encontrada"]})
            return None

        conflito = Reserva.objects.filter(
            sala=sala,
            data_inicio=dados['data_obj'],
            status__in=[Reserva.Status.APROVADA, Reserva.Status.PENDENTE],
        ).filter(
            Q(hora_inicio__lt=dados['hora_fim_obj']) & Q(hora_fim__gt=dados['hora_inicio_obj'])
        ).first()

        if conflito:
            return f"Reserva #{conflito.pk} ({conflito.hora_inicio}–{conflito.hora_fim})"
        return None

    def _parse_hora(self, valor):
        """Converte string de hora para objeto time."""
        if not valor:
            return None
        for fmt in ['%H:%M', '%H:%M:%S']:
            try:
                return datetime.strptime(valor.strip(), fmt).time()
            except ValueError:
                continue
        return None

    def _relatorio(self):
        return {
            'total_linhas': len(self.linhas_validas) + len(self.conflitos) + len(self.erros),
            'validas': len(self.linhas_validas),
            'conflitos': len(self.conflitos),
            'erros': len(self.erros),
            'detalhes_erros': self.erros,
            'detalhes_conflitos': self.conflitos,
            'avisos': self.avisos,
        }
