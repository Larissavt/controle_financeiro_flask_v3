/**
 * JavaScript customizado para Controle Financeiro Pessoal - VERSÃO 2
 * Validações em tempo real, formatação de valores e utilitários
 */

// ========== CONFIGURAÇÕES GLOBAIS ==========
const CONFIG = {
    debounceDelay: 300,
    alertAutoCloseTiming: 5000,
    maxValor: 999999.99,
    minValor: 0.01
};

// ========== INICIALIZAÇÃO ==========
document.addEventListener('DOMContentLoaded', function() {
    inicializarValidacoes();
    inicializarAlertas();
    inicializarTooltips();
    inicializarMascaras();
});

// ========== VALIDAÇÃO DE FORMULÁRIOS ==========
function inicializarValidacoes() {
    // Validar formulários Bootstrap
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Confirmar deleção
    const deleteButtons = document.querySelectorAll('button[type="submit"][onclick*="confirm"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            if (!confirm('Tem certeza? Esta ação não pode ser desfeita.')) {
                event.preventDefault();
            }
        });
    });

    // Validação em tempo real para descrição
    const descricaoInputs = document.querySelectorAll('input[name="descricao"]');
    descricaoInputs.forEach(input => {
        input.addEventListener('input', validarDescricaoRealTime);
    });

    // Validação em tempo real para valor
    const valorInputs = document.querySelectorAll('input[name="valor"]');
    valorInputs.forEach(input => {
        input.addEventListener('input', validarValorRealTime);
    });
}

// ========== VALIDAÇÃO DE DESCRIÇÃO EM TEMPO REAL ==========
function validarDescricaoRealTime(event) {
    const input = event.target;
    const valor = input.value.trim();
    const feedback = input.nextElementSibling;

    let valido = true;
    let mensagem = '';

    if (!valor) {
        mensagem = 'A descrição é obrigatória';
        valido = false;
    } else if (valor.length < 3) {
        mensagem = 'Mínimo 3 caracteres';
        valido = false;
    } else if (valor.length > 255) {
        mensagem = 'Máximo 255 caracteres';
        valido = false;
    }

    if (valido) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.style.display = 'none';
        }
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.textContent = mensagem;
            feedback.style.display = 'block';
        }
    }

    // Atualizar contador de caracteres se existir
    const counter = document.getElementById('descricaoCounter');
    if (counter) {
        counter.textContent = valor.length;
    }
}

// ========== VALIDAÇÃO DE VALOR EM TEMPO REAL ==========
function validarValorRealTime(event) {
    const input = event.target;
    const valor = input.value;
    const feedback = input.closest('.mb-3')?.querySelector('.invalid-feedback');
    const aviso = input.closest('.mb-3')?.querySelector('small.text-muted');

    let valido = true;
    let mensagem = '';
    let avisoTexto = '';

    if (!valor) {
        mensagem = 'O valor é obrigatório';
        valido = false;
    } else {
        const valorNum = parseFloat(valor);
        if (isNaN(valorNum) || valorNum <= 0) {
            mensagem = 'O valor deve ser positivo';
            valido = false;
        } else if (valorNum > CONFIG.maxValor) {
            mensagem = 'O valor é muito alto';
            valido = false;
        } else if (valorNum > 10000) {
            avisoTexto = '⚠️ Atenção: Este é um valor muito alto';
        }
    }

    const inputGroup = input.closest('.input-group') || input;
    if (valido) {
        inputGroup.classList.remove('is-invalid');
        inputGroup.classList.add('is-valid');
        if (feedback) {
            feedback.style.display = 'none';
        }
    } else {
        inputGroup.classList.remove('is-valid');
        inputGroup.classList.add('is-invalid');
        if (feedback) {
            feedback.textContent = mensagem;
            feedback.style.display = 'block';
        }
    }

    if (aviso) {
        aviso.textContent = avisoTexto;
    }
}

// ========== ALERTAS AUTO-FECHÁVEIS ==========
function inicializarAlertas() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, CONFIG.alertAutoCloseTiming);
    });
}

// ========== TOOLTIPS ==========
function inicializarTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ========== MÁSCARAS DE ENTRADA ==========
function inicializarMascaras() {
    // Máscara para campos de valor
    const valorInputs = document.querySelectorAll('input[type="number"][name="valor"]');
    valorInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                const valor = parseFloat(this.value);
                if (!isNaN(valor)) {
                    this.value = valor.toFixed(2);
                }
            }
        });
    });
}

// ========== FORMATAÇÃO DE MOEDA ==========
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// ========== FORMATAÇÃO DE DATA ==========
function formatarData(data) {
    if (typeof data === 'string') {
        data = new Date(data);
    }
    return new Intl.DateTimeFormat('pt-BR').format(data);
}

// ========== DEBOUNCE HELPER ==========
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// ========== THROTTLE HELPER ==========
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ========== NOTIFICAÇÃO CUSTOMIZADA ==========
function mostrarNotificacao(mensagem, tipo = 'info', duracao = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);

    if (duracao > 0) {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, duracao);
    }
}

// ========== LOADING STATE ==========
function setarLoadingButton(button, carregando = true) {
    if (carregando) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Carregando...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || 'Enviar';
    }
}

// ========== VERIFICAR CONEXÃO ==========
function verificarConexao() {
    return navigator.onLine;
}

// ========== COPIAR PARA CLIPBOARD ==========
function copiarParaClipboard(texto) {
    navigator.clipboard.writeText(texto).then(() => {
        mostrarNotificacao('Copiado para a área de transferência!', 'success', 2000);
    }).catch(() => {
        mostrarNotificacao('Erro ao copiar', 'danger');
    });
}

// ========== VALIDAR EMAIL ==========
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// ========== VALIDAR TELEFONE ==========
function validarTelefone(telefone) {
    const regex = /^\(?[0-9]{2}\)?[0-9]{4,5}[0-9]{4}$/;
    return regex.test(telefone.replace(/\D/g, ''));
}

// ========== OBTER PARÂMETRO URL ==========
function obterParametroUrl(nome) {
    const params = new URLSearchParams(window.location.search);
    return params.get(nome);
}

// ========== REDIRECIONAR COM DELAY ==========
function redirecionarComDelay(url, delay = 2000) {
    setTimeout(() => {
        window.location.href = url;
    }, delay);
}

// ========== SALVAR NO LOCALSTORAGE ==========
function salvarNoStorage(chave, valor) {
    try {
        localStorage.setItem(chave, JSON.stringify(valor));
        return true;
    } catch (e) {
        console.error('Erro ao salvar no storage:', e);
        return false;
    }
}

// ========== RECUPERAR DO LOCALSTORAGE ==========
function recuperarDoStorage(chave) {
    try {
        const valor = localStorage.getItem(chave);
        return valor ? JSON.parse(valor) : null;
    } catch (e) {
        console.error('Erro ao recuperar do storage:', e);
        return null;
    }
}

// ========== LIMPAR LOCALSTORAGE ==========
function limparStorage(chave = null) {
    try {
        if (chave) {
            localStorage.removeItem(chave);
        } else {
            localStorage.clear();
        }
        return true;
    } catch (e) {
        console.error('Erro ao limpar storage:', e);
        return false;
    }
}

// ========== DETECTAR DISPOSITIVO ==========
const DetectorDispositivo = {
    isMobile: () => /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
    isTablet: () => /iPad|Android/i.test(navigator.userAgent) && !/iPhone|iPod/i.test(navigator.userAgent),
    isDesktop: () => !/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
    getTipo: function() {
        if (this.isMobile()) return 'mobile';
        if (this.isTablet()) return 'tablet';
        return 'desktop';
    }
};

// ========== CONSOLE LOG PARA DEBUG ==========
console.log('Controle Financeiro Pessoal - Script v2 carregado com sucesso!');
console.log('Dispositivo detectado:', DetectorDispositivo.getTipo());
