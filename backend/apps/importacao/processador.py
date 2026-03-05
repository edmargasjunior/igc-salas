"""
Processador de CSV para importação de planejamento semestral.
Formato esperado:
sala_codigo,data,hora_inicio,hora_fim,disciplina_codigo,professor_siape,turma_codigo
IGC-101,2025-03-03,08:00,09:40,GEO001,1234567,T01
"""
import csv
import io
from datetime import datetime
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger('apps.importacao')


class CSVImportador:
    """
    Processa arquivo CSV de planejamento semestral.
    Valida cada linha, detecta conflitos e cria reservas.
    """

    COLUNAS_OBRIGATORIAS = [
        'sala_codigo', 'data', 'hora_inicio', 'hora_fim',
        'disciplina_codigo', 'professor_siape', 'turma_codigo'
    ]

    def __init__(self, importacao, usuario):
        self.importacao = importacao
        self.usuario = usuario
        self.relatorio = []
        self.erros = 0
        self.sucessos = 0
        self.conflitos = 0

    def processar(self, arquivo_csv, confirmar=False):
        """
        Processa o CSV em modo simulação ou confirmação.
        confirmar=False: apenas valida e retorna relatório
        confirmar=True: efetivamente cria as reservas
        """
        from apps.estrutura.models import Sala
        from apps.academico.models import Disciplina, Professor, Turma
        from apps.reservas.models import Reserva

        try:
            conteudo = arquivo_csv.read().decode('utf-8-sig')
        except UnicodeDecodeError:
            conteudo = arquivo_csv.read().decode('latin-1')

        reader = csv.DictReader(io.StringIO(conteudo))

        # Verificar colunas
        if not reader.fieldnames:
            return {'erro': 'Arquivo CSV vazio ou inválido.'}

        colunas_faltando = [c for c in self.COLUNAS_OBRIGATORIAS if c not in reader.fieldnames]
        if colunas_faltando:
            return {
                'erro': f'Colunas obrigatórias ausentes: {", ".join(colunas_faltando)}',
                'colunas_encontradas': list(reader.fieldnames),
            }

        linhas = list(reader)
        self.importacao.total_linhas = len(linhas)
        self.importacao.save(update_fields=['total_linhas'])

        for num, linha in enumerate(linhas, start=2):
            resultado = self._processar_linha(num, linha, confirmar)
            self.relatorio.append(resultado)

            if resultado['status'] == 'ok':
                self.sucessos += 1
            elif resultado['status'] == 'conflito':
                self.conflitos += 1
            else:
                self.erros += 1

        self.importacao.linhas_sucesso = self.sucessos
        self.importacao.linhas_erro = self.erros
        self.importacao.linhas_conflito = self.conflitos
        self.importacao.relatorio = self.relatorio
        self.importacao.status = 'concluido'
        self.importacao.concluido_em = timezone.now()
        self.importacao.save()

        return {
            'total': len(linhas),
            'sucesso': self.sucessos,
            'erros': self.erros,
            'conflitos': self.conflitos,
            'relatorio': self.relatorio[:100],
        }

    def _processar_linha(self, num, linha, confirmar):
        from apps.estrutura.models import Sala
        from apps.academico.models import Disciplina, Professor, Turma
        from apps.reservas.models import Reserva
        from datetime import date, time

        resultado = {'linha': num, 'status': 'ok', 'mensagem': '', 'dados': {}}

        try:
            # Buscar sala
            sala_codigo = linha.get('sala_codigo', '').strip()
            try:
                sala = Sala.objects.get(codigo=sala_codigo, ativo=True)
            except Sala.DoesNotExist:
                return {**resultado, 'status': 'erro', 'mensagem': f'Sala "{sala_codigo}" não encontrada.'}

            # Parsear data
            data_str = linha.get('data', '').strip()
            try:
                data = datetime.strptime(data_str, '%Y-%m-%d').date()
            except ValueError:
                return {**resultado, 'status': 'erro', 'mensagem': f'Data inválida: "{data_str}" (use YYYY-MM-DD)'}

            # Parsear horários
            def parse_time(s):
                for fmt in ['%H:%M', '%H:%M:%S']:
                    try:
                        return datetime.strptime(s.strip(), fmt).time()
                    except ValueError:
                        continue
                raise ValueError(f'Horário inválido: {s}')

            try:
                hora_inicio = parse_time(linha.get('hora_inicio', ''))
                hora_fim = parse_time(linha.get('hora_fim', ''))
            except ValueError as e:
                return {**resultado, 'status': 'erro', 'mensagem': str(e)}

            if hora_fim <= hora_inicio:
                return {**resultado, 'status': 'erro', 'mensagem': 'Hora de fim deve ser após hora de início.'}

            # Verificar conflito
            from django.db.models import Q
            conflito_qs = Reserva.objects.filter(
                sala=sala,
                data_inicio=data,
                status__in=['aprovada', 'pendente']
            ).filter(
                Q(hora_inicio__lt=hora_fim) & Q(hora_fim__gt=hora_inicio)
            )

            if conflito_qs.exists():
                c = conflito_qs.first()
                return {**resultado,
                    'status': 'conflito',
                    'mensagem': f'Conflito com reserva #{c.pk} ({c.hora_inicio}-{c.hora_fim})',
                    'dados': {'sala': sala_codigo, 'data': data_str}
                }

            # Buscar turma/disciplina
            disc_codigo = linha.get('disciplina_codigo', '').strip()
            siape = linha.get('professor_siape', '').strip()
            turma_codigo = linha.get('turma_codigo', '').strip()

            turma = None
            try:
                from apps.academico.models import Professor
                prof = Professor.objects.get(siape=siape)
                from apps.academico.models import Disciplina
                disc = Disciplina.objects.get(codigo=disc_codigo)
                turma, _ = Turma.objects.get_or_create(
                    disciplina=disc,
                    professor=prof,
                    codigo=turma_codigo,
                    ano=data.year,
                    semestre='1' if data.month <= 6 else '2',
                )
            except Exception:
                pass

            resultado['dados'] = {
                'sala': sala_codigo, 'data': data_str,
                'hora_inicio': str(hora_inicio), 'hora_fim': str(hora_fim),
                'disciplina': disc_codigo,
            }

            # Criar reserva se confirmar
            if confirmar:
                Reserva.objects.create(
                    sala=sala,
                    solicitante=self.usuario,
                    turma=turma,
                    tipo='pontual',
                    data_inicio=data,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    motivo=f'Importado via CSV - {disc_codigo}',
                    status='aprovada',
                    aprovado_por=self.usuario,
                )

            return {**resultado, 'status': 'ok', 'mensagem': f'Linha {num} OK'}

        except Exception as e:
            logger.error(f"Erro processando linha {num}: {e}")
            return {**resultado, 'status': 'erro', 'mensagem': f'Erro interno: {str(e)}'}
