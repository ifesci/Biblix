/**
 * Perfil Photo Handler
 *
 * Gerencia o fluxo de seleção e crop de foto de perfil
 * Abre o seletor de arquivos diretamente ao clicar na foto ou botão
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos
    const photoInput = document.getElementById('hidden-photo-input');
    const profilePhoto = document.getElementById('profile-photo');
    const changePhotoBtn = document.getElementById('btn-change-photo');

    // Configuração do modal (deve existir no window)
    const modalConfig = window.config_modalFotoPerfil;

    if (!photoInput || !modalConfig) {
        console.warn('Elementos necessários para photo handler não encontrados');
        return;
    }

    // Função para abrir o seletor de arquivos
    function openFileSelector() {
        photoInput.click();
    }

    // Adicionar click handler na foto de perfil (se existir)
    if (profilePhoto) {
        profilePhoto.style.cursor = 'pointer';
        profilePhoto.addEventListener('click', openFileSelector);
    }

    // Adicionar click handler no botão de alterar foto
    if (changePhotoBtn) {
        changePhotoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openFileSelector();
        });
    }

    // Quando um arquivo for selecionado
    photoInput.addEventListener('change', async function(e) {
        const file = e.target.files[0];

        if (!file) return;

        try {
            // 1. PREPARAR a imagem ANTES de abrir o modal
            // Isso carrega a imagem e define o tamanho do container
            await prepareImageForModal(
                modalConfig.modalId,
                file,
                modalConfig.maxFileSizeMB
            );

            // 2. AGORA abrir o modal (imagem já está carregada e container já está dimensionado)
            const modalElement = document.getElementById(modalConfig.modalId);
            const modal = new bootstrap.Modal(modalElement);
            modal.show();

            // 3. Quando o modal estiver completamente visível, INICIALIZAR o Cropper
            modalElement.addEventListener('shown.bs.modal', function() {
                initializeCropperInModal(
                    modalConfig.modalId,
                    modalConfig.aspectRatio
                );
            }, { once: true });

        } catch (error) {
            // Se houver erro (arquivo inválido, muito grande, etc.), exibir mensagem
            alert(error);
            photoInput.value = '';
        }
    });

    // Resetar o input quando o modal for fechado
    document.getElementById(modalConfig.modalId).addEventListener('hidden.bs.modal', function() {
        photoInput.value = '';
    });
});
