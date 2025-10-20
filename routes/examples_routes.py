from fastapi import APIRouter, Request
from util.template_util import criar_templates

router = APIRouter(prefix="/examples")
templates_home = criar_templates("templates")


@router.get("")
async def home(request: Request):
    """
    Página inicial de exemplos
    """
    return templates_home.TemplateResponse(
        "examples/index.html",
        {"request": request}
    )


@router.get("/form-fields")
async def form_fields_demo(request: Request):
    """
    Página de demonstração da macro de campos de formulário
    """
    return templates_home.TemplateResponse(
        "examples/form_fields_demo.html",
        {"request": request}
    )


@router.get("/cards-grid")
async def cards_grid_demo(request: Request):
    """
    Página de demonstração de grid de cards responsivo
    """
    return templates_home.TemplateResponse(
        "examples/cards_grid.html",
        {"request": request}
    )


@router.get("/bootswatch")
async def bootswatch_demo(request: Request):
    """
    Página de demonstração de temas Bootswatch
    """
    return templates_home.TemplateResponse(
        "examples/bootswatch.html",
        {"request": request}
    )


@router.get("/product-detail")
async def product_detail_demo(request: Request):
    """
    Página de demonstração de detalhes de produto e-commerce
    """
    return templates_home.TemplateResponse(
        "examples/product_detail.html",
        {"request": request}
    )


@router.get("/service-detail")
async def service_detail_demo(request: Request):
    """
    Página de demonstração de detalhes de serviço profissional
    """
    return templates_home.TemplateResponse(
        "examples/service_detail.html",
        {"request": request}
    )


@router.get("/profile-detail")
async def profile_detail_demo(request: Request):
    """
    Página de demonstração de perfil de pessoa
    """
    return templates_home.TemplateResponse(
        "examples/profile_detail.html",
        {"request": request}
    )


@router.get("/property-detail")
async def property_detail_demo(request: Request):
    """
    Página de demonstração de detalhes de imóvel
    """
    return templates_home.TemplateResponse(
        "examples/property_detail.html",
        {"request": request}
    )


@router.get("/table-list")
async def table_list_demo(request: Request):
    """
    Página de demonstração de tabela com listagem de dados
    """
    # Dados mockados para demonstração
    produtos = [
        {"id": 1, "nome": "Notebook Dell Inspiron 15", "categoria": "Informática", "preco": 3499.90, "estoque": 75, "ativo": True},
        {"id": 2, "nome": "Mouse Gamer RGB", "categoria": "Periféricos", "preco": 129.90, "estoque": 150, "ativo": True},
        {"id": 3, "nome": "Teclado Mecânico", "categoria": "Periféricos", "preco": 349.90, "estoque": 45, "ativo": True},
        {"id": 4, "nome": "Monitor LG 27\" 4K", "categoria": "Monitores", "preco": 1899.90, "estoque": 12, "ativo": True},
        {"id": 5, "nome": "Webcam Full HD", "categoria": "Periféricos", "preco": 249.90, "estoque": 8, "ativo": True},
        {"id": 6, "nome": "Headset Bluetooth", "categoria": "Áudio", "preco": 199.90, "estoque": 92, "ativo": True},
        {"id": 7, "nome": "SSD 1TB NVMe", "categoria": "Armazenamento", "preco": 449.90, "estoque": 38, "ativo": True},
        {"id": 8, "nome": "Memória RAM 16GB", "categoria": "Componentes", "preco": 299.90, "estoque": 5, "ativo": False},
        {"id": 9, "nome": "Placa de Vídeo RTX 3060", "categoria": "Componentes", "preco": 2299.90, "estoque": 3, "ativo": True},
        {"id": 10, "nome": "Cadeira Gamer", "categoria": "Mobília", "preco": 899.90, "estoque": 18, "ativo": True},
    ]

    return templates_home.TemplateResponse(
        "examples/table_list.html",
        {"request": request, "produtos": produtos}
    )
