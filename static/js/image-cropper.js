/**
 * Image Cropper
 *
 * Sistema reutilizável de crop de imagens usando Cropper.js
 *
 * Uso:
 * 1. Incluir Cropper.js no template: <link href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.css" rel="stylesheet">
 * 2. Incluir script: <script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.js"></script>
 * 3. Incluir este arquivo: <script src="/static/js/image-cropper.js"></script>
 * 4. Configurar window.config_{modalId} com modalId, aspectRatio e maxFileSizeMB
 */

// Armazenar instâncias do Cropper para cada modal
const cropperInstances = {};

/**
 * Prepara uma imagem para o modal SEM inicializar o Cropper
 * Útil para pré-carregar antes de abrir o modal
 *
 * @param {string} modalId - ID do modal
 * @param {File} file - Arquivo de imagem
 * @param {number} maxFileSizeMB - Tamanho máximo em MB (default: 5)
 * @returns {Promise} - Resolve quando a imagem estiver carregada
 */
function prepareImageForModal(modalId, file, maxFileSizeMB = 5) {
    return new Promise((resolve, reject) => {
        const uploadSection = document.getElementById(`upload-section-${modalId}`);
        const cropperContainer = document.getElementById(`cropper-container-${modalId}`);
        const cropperImage = document.getElementById(`cropper-image-${modalId}`);
        const cropperImageArea = document.getElementById(`cropper-image-area-${modalId}`);
        const btnSubmit = document.getElementById(`btn-submit-${modalId}`);

        if (!file) {
            reject('Nenhum arquivo fornecido');
            return;
        }

        // Validar tamanho
        const maxBytes = maxFileSizeMB * 1024 * 1024;
        if (file.size > maxBytes) {
            reject(`Arquivo muito grande! Tamanho máximo: ${maxFileSizeMB}MB`);
            return;
        }

        // Validar tipo
        if (!file.type.startsWith('image/')) {
            reject('Por favor, selecione um arquivo de imagem válido.');
            return;
        }

        // Ler arquivo
        const reader = new FileReader();
        reader.onload = function(event) {
            // Ocultar seção de upload e mostrar cropper
            if (uploadSection) uploadSection.classList.add('d-none');
            if (cropperContainer) cropperContainer.classList.remove('d-none');
            if (btnSubmit) btnSubmit.disabled = false;

            // Definir imagem no cropper
            cropperImage.src = event.target.result;

            // Pré-calcular e aplicar altura ideal ANTES do modal abrir
            // Usar estimativa baseada em viewport já que o modal ainda não está visível
            const viewportHeight = window.innerHeight;
            const estimatedHeight = Math.max(200, Math.min(600, viewportHeight * 0.5));
            cropperImageArea.style.height = `${estimatedHeight}px`;

            // Aguardar a imagem carregar completamente
            cropperImage.onload = function() {
                resolve();
            };
            cropperImage.onerror = function() {
                reject('Erro ao carregar a imagem');
            };
        };
        reader.onerror = function() {
            reject('Erro ao ler o arquivo');
        };
        reader.readAsDataURL(file);
    });
}

/**
 * Inicializa o Cropper no modal (deve ser chamado após o modal estar visível)
 *
 * @param {string} modalId - ID do modal
 * @param {number} aspectRatio - Proporção do crop (default: 1.0)
 * @param {Function} onReady - Callback chamado quando o cropper estiver pronto (opcional)
 */
function initializeCropperInModal(modalId, aspectRatio = 1.0, onReady = null) {
    const cropperImage = document.getElementById(`cropper-image-${modalId}`);
    const previewImage = document.getElementById(`preview-${modalId}`);

    if (!cropperImage || !cropperImage.src) {
        console.error(`Imagem não preparada para o modal ${modalId}`);
        return;
    }

    // Destruir cropper anterior se existir
    if (cropperInstances[modalId]) {
        cropperInstances[modalId].destroy();
    }

    // Inicializar Cropper.js
    cropperInstances[modalId] = new Cropper(cropperImage, {
        aspectRatio: aspectRatio,
        viewMode: 1,  // Permite crop box crescer até os limites do container
        dragMode: 'move',
        autoCropArea: 0.8,  // Área inicial de 80% para dar espaço para expansão
        restore: false,
        guides: true,
        center: true,
        highlight: false,
        cropBoxMovable: true,
        cropBoxResizable: true,
        toggleDragModeOnDblclick: false,
        minContainerWidth: 200,  // Container mínimo
        minContainerHeight: 200,
        ready: function() {
            // Ajustar tamanho baseado nas dimensões reais do modal agora visível
            adjustCropperContainerSize(modalId);
            // Chamar callback se fornecido
            if (onReady && typeof onReady === 'function') {
                onReady();
            }
        },
        crop: function(event) {
            // Atualizar preview em tempo real
            if (previewImage) updatePreview(modalId, previewImage);
        }
    });
}

/**
 * Carrega uma imagem de um arquivo File e inicializa o cropper
 * Função pública que pode ser chamada externamente
 *
 * @param {string} modalId - ID do modal
 * @param {File} file - Arquivo de imagem
 * @param {number} aspectRatio - Proporção do crop (default: 1.0)
 * @param {number} maxFileSizeMB - Tamanho máximo em MB (default: 5)
 * @param {Function} onReady - Callback chamado quando o cropper estiver pronto (opcional)
 */
function loadImageFromFile(modalId, file, aspectRatio = 1.0, maxFileSizeMB = 5, onReady = null) {
    const uploadSection = document.getElementById(`upload-section-${modalId}`);
    const cropperContainer = document.getElementById(`cropper-container-${modalId}`);
    const cropperImage = document.getElementById(`cropper-image-${modalId}`);
    const previewImage = document.getElementById(`preview-${modalId}`);
    const btnSubmit = document.getElementById(`btn-submit-${modalId}`);

    if (!file) return;

    // Validar tamanho
    const maxBytes = maxFileSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
        alert(`Arquivo muito grande! Tamanho máximo: ${maxFileSizeMB}MB`);
        return;
    }

    // Validar tipo
    if (!file.type.startsWith('image/')) {
        alert('Por favor, selecione um arquivo de imagem válido.');
        return;
    }

    // Ler arquivo
    const reader = new FileReader();
    reader.onload = function(event) {
        // Ocultar seção de upload e mostrar cropper
        if (uploadSection) uploadSection.classList.add('d-none');
        if (cropperContainer) cropperContainer.classList.remove('d-none');
        if (btnSubmit) btnSubmit.disabled = false;

        // Definir imagem no cropper
        cropperImage.src = event.target.result;

        // Destruir cropper anterior se existir
        if (cropperInstances[modalId]) {
            cropperInstances[modalId].destroy();
        }

        // Inicializar Cropper.js
        cropperInstances[modalId] = new Cropper(cropperImage, {
            aspectRatio: aspectRatio,
            viewMode: 1,  // Permite crop box crescer até os limites do container
            dragMode: 'move',
            autoCropArea: 0.8,  // Área inicial de 80% para dar espaço para expansão
            restore: false,
            guides: true,
            center: true,
            highlight: false,
            cropBoxMovable: true,
            cropBoxResizable: true,
            toggleDragModeOnDblclick: false,
            minContainerWidth: 200,  // Container mínimo
            minContainerHeight: 200,
            ready: function() {
                // Aguardar 100ms para garantir que o DOM foi atualizado
                setTimeout(() => {
                    adjustCropperContainerSize(modalId);
                    // Chamar callback se fornecido
                    if (onReady && typeof onReady === 'function') {
                        onReady();
                    }
                }, 100);
            },
            crop: function(event) {
                // Atualizar preview em tempo real
                if (previewImage) updatePreview(modalId, previewImage);
            }
        });
    };
    reader.readAsDataURL(file);
}

/**
 * Inicializa o cropper para um modal específico
 */
function initImageCropper(modalId, aspectRatio = 1.0, maxFileSizeMB = 5) {
    const inputFile = document.getElementById(`input-${modalId}`);
    const uploadSection = document.getElementById(`upload-section-${modalId}`);
    const cropperContainer = document.getElementById(`cropper-container-${modalId}`);
    const cropperImage = document.getElementById(`cropper-image-${modalId}`);
    const previewImage = document.getElementById(`preview-${modalId}`);
    const btnSubmit = document.getElementById(`btn-submit-${modalId}`);
    const fotoBase64Input = document.getElementById(`foto-base64-${modalId}`);
    const form = document.getElementById(`form-${modalId}`);

    if (!cropperContainer || !cropperImage) {
        console.error(`Elementos do modal ${modalId} não encontrados`);
        return;
    }

    // Evento: Seleção de arquivo (apenas se input file existir)
    if (inputFile) {
        inputFile.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                loadImageFromFile(modalId, file, aspectRatio, maxFileSizeMB);
            }
        });
    }

    // Evento: Submit do formulário
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            if (!cropperInstances[modalId]) {
                alert('Nenhuma imagem selecionada');
                return;
            }

            // Obter canvas da imagem cropada
            const canvas = cropperInstances[modalId].getCroppedCanvas({
                maxWidth: 1000,
                maxHeight: 1000,
                fillColor: '#fff',
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high'
            });

            // Converter para base64 (JPEG com qualidade 90)
            const base64 = canvas.toDataURL('image/jpeg', 0.9);

            // Definir no campo hidden
            fotoBase64Input.value = base64;

            // Submeter formulário
            form.submit();
        });
    }

    // Evento: Reset ao fechar modal
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', function() {
            resetCropper(modalId, uploadSection, cropperContainer, inputFile, btnSubmit);
        });
    }
}

/**
 * Calcula a altura disponível para a área de imagem do cropper
 * Mede os elementos reais do DOM para precisão
 */
function calculateCropperImageHeight(modalId) {
    // Obter elementos
    const modalElement = document.getElementById(modalId);
    const modalHeader = modalElement?.querySelector('.modal-header');
    const modalBody = modalElement?.querySelector('.modal-body');
    const controlsArea = document.getElementById(`cropper-controls-area-${modalId}`);

    if (!modalElement || !modalHeader || !modalBody || !controlsArea) {
        console.warn(`Elementos do modal ${modalId} não encontrados para cálculo de altura`);
        return 300; // Valor padrão de fallback
    }

    // Medir alturas reais
    const viewportHeight = window.innerHeight;
    const headerHeight = modalHeader.offsetHeight;
    const controlsHeight = controlsArea.offsetHeight;

    // Pegar padding do modal-body
    const bodyStyles = window.getComputedStyle(modalBody);
    const bodyPaddingTop = parseFloat(bodyStyles.paddingTop) || 0;
    const bodyPaddingBottom = parseFloat(bodyStyles.paddingBottom) || 0;

    // Margem de segurança para espaçamentos internos e scroll
    const safetyMargin = 100;

    // Calcular altura disponível
    const availableHeight = viewportHeight - headerHeight - controlsHeight - bodyPaddingTop - bodyPaddingBottom - safetyMargin;

    // Aplicar limites: mínimo 200px, máximo 600px
    const finalHeight = Math.max(200, Math.min(600, availableHeight));

    return finalHeight;
}

/**
 * Ajusta o tamanho do container do cropper dinamicamente
 */
function adjustCropperContainerSize(modalId) {
    const cropperImageArea = document.getElementById(`cropper-image-area-${modalId}`);
    if (!cropperImageArea) return;

    // Calcular altura usando medição real dos elementos
    const calculatedHeight = calculateCropperImageHeight(modalId);

    // Aplicar altura calculada
    cropperImageArea.style.height = `${calculatedHeight}px`;

    // Forçar o cropper a recalcular suas dimensões
    if (cropperInstances[modalId]) {
        cropperInstances[modalId].resize();
    }
}

/**
 * Atualiza o preview da imagem cropada
 */
function updatePreview(modalId, previewImage) {
    if (!cropperInstances[modalId]) return;

    const canvas = cropperInstances[modalId].getCroppedCanvas({
        width: 120,
        height: 120,
        imageSmoothingEnabled: true,
        imageSmoothingQuality: 'high'
    });

    if (canvas) {
        previewImage.src = canvas.toDataURL('image/jpeg', 0.9);
    }
}

/**
 * Reseta o cropper para estado inicial
 */
function resetCropper(modalId, uploadSection, cropperContainer, inputFile, btnSubmit) {
    // Destruir cropper
    if (cropperInstances[modalId]) {
        cropperInstances[modalId].destroy();
        delete cropperInstances[modalId];
    }

    // Resetar UI para estado inicial
    if (uploadSection) uploadSection.classList.remove('d-none');
    if (cropperContainer) cropperContainer.classList.add('d-none');
    if (inputFile) inputFile.value = '';
    if (btnSubmit) btnSubmit.disabled = true;
}

/**
 * Auto-inicialização de modais com configuração
 */
document.addEventListener('DOMContentLoaded', function() {
    // Procurar por todas as configurações de modal no window
    for (const key in window) {
        if (key.startsWith('config_modal')) {
            const config = window[key];
            if (config && config.modalId) {
                initImageCropper(
                    config.modalId,
                    config.aspectRatio || 1.0,
                    config.maxFileSizeMB || 5
                );
            }
        }
    }

    // Ajustar tamanho do cropper quando a janela for redimensionada (com debounce)
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            for (const modalId in cropperInstances) {
                if (cropperInstances[modalId]) {
                    adjustCropperContainerSize(modalId);
                }
            }
        }, 150);
    });
});
