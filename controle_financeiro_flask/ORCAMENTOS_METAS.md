# Orçamentos e Metas - Guia Completo

## 📋 Visão Geral

A funcionalidade de **Orçamentos e Metas** permite que você defina limites de gastos por categoria, acompanhe o progresso em tempo real e receba alertas visuais quando estiver próximo ou ultrapassar seus limites.

---

## 🎯 Funcionalidades Principais

### 1. Criar Orçamentos
- Defina um limite de gastos para cada categoria
- Configure o percentual de alerta (padrão: 80%)
- Crie orçamentos para qualquer mês/ano
- Apenas um orçamento por categoria/mês/ano

### 2. Visualizar Orçamentos
- Dashboard com resumo visual
- Barras de progresso coloridas
- Status em tempo real (Ok, Aviso, Excedido)
- Informações de dias restantes no mês

### 3. Alertas Inteligentes
- Alerta ao atingir o percentual configurado
- Alerta ao exceder o limite
- Projeção de gastos até o final do mês
- Aviso se a projeção ultrapassar o limite

### 4. Histórico
- Visualize orçamentos de meses anteriores
- Compare gastos entre períodos
- Análise de conformidade

---

## 🚀 Como Usar

### Criar um Novo Orçamento

1. **Acesse a página de Orçamentos**
   - Clique em "Orçamentos" no menu principal
   - Ou acesse: `/orcamentos`

2. **Clique em "Novo Orçamento"**
   - Botão azul no canto superior direito

3. **Preencha o Formulário**
   - **Categoria**: Selecione a categoria para o orçamento
   - **Limite Mensal**: Valor máximo que deseja gastar
   - **Percentual de Alerta**: Quando receber aviso (padrão: 80%)
   - **Mês e Ano**: Período do orçamento

4. **Clique em "Criar Orçamento"**
   - Seu orçamento foi criado com sucesso!

### Editar um Orçamento

1. **Na página de Orçamentos, clique em "Editar"**
   - Botão amarelo ao lado do orçamento

2. **Modifique os Valores**
   - Limite mensal
   - Percentual de alerta

3. **Clique em "Atualizar Orçamento"**

### Deletar um Orçamento

1. **Na página de Orçamentos, clique em "Deletar"**
   - Botão vermelho ao lado do orçamento

2. **Confirme a Deleção**
   - Clique em "Ok" na confirmação

### Visualizar Histórico

1. **Na página de Orçamentos, clique em "Ver Histórico"**
   - Ou acesse: `/orcamentos/historico`

2. **Selecione um Período**
   - Escolha mês e ano
   - Clique em "Visualizar"

3. **Analise os Dados**
   - Compare gastos com limites
   - Veja o status de cada orçamento

---

## 📊 Entendendo os Status

### ✅ Status OK (Verde)
- Gasto está abaixo do percentual de alerta
- Tudo sob controle
- Nenhuma ação necessária

### ⚠️ Status Aviso (Amarelo)
- Gasto atingiu o percentual de alerta
- Exemplo: Limite R$ 1.000, Alerta 80% = Aviso em R$ 800
- Recomendação: Reduza gastos ou aumente o limite

### ❌ Status Excedido (Vermelho)
- Gasto ultrapassou o limite
- Você está gastando mais do que planejado
- Ação necessária: Ajuste o orçamento ou reduza gastos

---

## 💡 Cálculos e Fórmulas

### Percentual Usado
```
Percentual = (Gasto Atual / Limite) × 100
```

### Valor Restante
```
Restante = Limite - Gasto Atual
```

### Projeção de Gastos
```
Dias Passados = Dia Atual do Mês
Média Diária = Gasto Atual / Dias Passados
Projeção = Gasto Atual + (Média Diária × Dias Restantes)
```

### Alerta de Projeção
Se a projeção ultrapassar o limite, você receberá um aviso com o valor estimado de excesso.

---

## 📈 Exemplo Prático

**Cenário**: Você define um orçamento de R$ 1.000 para Alimentação em Novembro, com alerta em 80%.

| Data | Gasto | Total | Percentual | Status | Ação |
|------|-------|-------|-----------|--------|------|
| 10/11 | R$ 200 | R$ 200 | 20% | ✅ Ok | Continuar |
| 15/11 | R$ 400 | R$ 600 | 60% | ✅ Ok | Continuar |
| 20/11 | R$ 200 | R$ 800 | 80% | ⚠️ Aviso | Reduzir gastos |
| 25/11 | R$ 300 | R$ 1.100 | 110% | ❌ Excedido | Ajustar orçamento |

---

## 🎓 Dicas para Definir Bons Orçamentos

### 1. Analise Histórico
- Revise seus gastos dos últimos 3 meses
- Calcule a média mensal
- Use como base para o orçamento

### 2. Seja Realista
- Não defina limites muito baixos
- Deixe margem para imprevistos
- Comece com 80% de alerta

### 3. Revise Regularmente
- Ajuste mensalmente conforme necessário
- Aumente limites se necessário
- Reduza se estiver economizando

### 4. Use Múltiplas Categorias
- Crie orçamentos para todas as categorias
- Priorize as maiores despesas
- Comece com as mais críticas

### 5. Estabeleça Metas Progressivas
- Mês 1: Apenas acompanhar
- Mês 2: Reduzir em 5%
- Mês 3: Reduzir em 10%

---

## 🔧 Integração com Dashboard

### Resumo no Dashboard Principal
O dashboard principal agora exibe:
- Resumo de orçamentos do mês
- Alertas de orçamentos
- Link rápido para gerenciar orçamentos

### Filtro de Transações
Os filtros de transações consideram os orçamentos:
- Visualize gastos por categoria
- Compare com o orçamento definido
- Identifique categorias problemáticas

---

## 📱 Responsividade Mobile

A funcionalidade de orçamentos é totalmente responsiva:
- Cards adaptáveis para telas pequenas
- Barras de progresso visíveis em mobile
- Formulários otimizados para toque
- Tabelas com scroll horizontal

---

## 🔐 Segurança

### Proteções Implementadas
- Verificação de propriedade (usuário_id)
- Validação de valores no servidor
- Proteção contra SQL Injection
- Confirmação antes de deletar

### Dados Protegidos
- Orçamentos isolados por usuário
- Não é possível editar orçamentos de outros usuários
- Histórico preservado para auditoria

---

## ⚙️ Configuração Técnica

### Modelo de Dados
```python
class Orcamento(db.Model):
    id                  # ID único
    usuario_id          # Usuário proprietário
    categoria_id        # Categoria do orçamento
    mes                 # Mês (1-12)
    ano                 # Ano (2020-2100)
    limite              # Limite de gastos
    alerta_percentual   # Percentual de alerta (1-100)
    data_criacao        # Data de criação
    data_atualizacao    # Data da última atualização
```

### Métodos Disponíveis
```python
orcamento.get_gasto_atual()        # Retorna gasto atual
orcamento.get_percentual_usado()   # Retorna percentual (0-100)
orcamento.get_restante()           # Retorna valor restante
orcamento.get_status()             # Retorna status (ok/aviso/excedido)
orcamento.get_status_badge()       # Retorna badge para exibição
orcamento.get_dias_restantes_mes() # Retorna dias restantes
orcamento.get_projecao_gasto()     # Retorna projeção até fim do mês
orcamento.get_alerta_projecao()    # Retorna alerta de projeção
```

### Rotas Disponíveis
```
GET  /orcamentos                              # Listar orçamentos
GET  /orcamentos/criar                        # Formulário criar
POST /orcamentos/criar                        # Salvar novo
GET  /orcamentos/<id>/editar                  # Formulário editar
POST /orcamentos/<id>/editar                  # Salvar edição
POST /orcamentos/<id>/deletar                 # Deletar
GET  /orcamentos/historico                    # Ver histórico
GET  /api/orcamentos/resumo                   # API resumo
GET  /api/orcamentos/<id>/detalhes            # API detalhes
GET  /api/orcamentos/alertas                  # API alertas
```

---

## 🐛 Troubleshooting

### Problema: Orçamento não aparece
**Solução**: Verifique se o mês/ano está correto. Orçamentos são filtrados por período.

### Problema: Alerta não aparece
**Solução**: Verifique se o gasto atingiu o percentual de alerta. Alertas aparecem apenas quando atingem o limite.

### Problema: Projeção incorreta
**Solução**: A projeção é calculada com base na média diária. Espere alguns dias para ter uma projeção mais precisa.

### Problema: Não consigo editar
**Solução**: Apenas o criador do orçamento pode editá-lo. Verifique se está logado com a conta correta.

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Consulte este guia
2. Verifique os logs do servidor
3. Revise o código em `app/routes_orcamentos.py`
4. Consulte a documentação de modelos em `app/models_v3.py`

---

## ✅ Checklist de Implementação

- [ ] Copiar `models_v3.py` para `models.py`
- [ ] Copiar `routes_orcamentos.py` para `app/`
- [ ] Copiar templates para `templates/`
- [ ] Atualizar `app/__init__.py` com nova blueprint
- [ ] Atualizar `base.html` com link para orçamentos
- [ ] Testar criação de orçamento
- [ ] Testar edição de orçamento
- [ ] Testar deleção de orçamento
- [ ] Testar visualização de histórico
- [ ] Testar APIs
- [ ] Testar em mobile
- [ ] Verificar segurança

---

## 🎉 Próximas Melhorias

- [ ] Gráficos de tendência de orçamentos
- [ ] Exportação de relatórios
- [ ] Notificações por email
- [ ] Orçamentos recorrentes
- [ ] Metas de economia
- [ ] Comparação com períodos anteriores

---

**Versão**: 3.0  
**Data**: Novembro 2024  
**Status**: ✅ Pronto para Produção
