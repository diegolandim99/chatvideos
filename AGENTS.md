# AGENTS.md — Guia para Desenvolvimento de Skills do ClipAI

Este documento descreve como criar e registrar novas **skills** no ecossistema ClipAI.

## O que é uma Skill?

Uma skill é um módulo Python independente que implementa uma capacidade específica do agente.
Cada skill deve ser:
- **Autocontida**: sem dependências não declaradas
- **Interativa**: aceitar inputs do usuário via `input()`
- **Resiliente**: tratar erros com mensagens amigáveis em português

## Estrutura de uma Skill

```python
# skills/minha_skill/__init__.py

def run(video_path=None, **kwargs):
    """
    Ponto de entrada da skill.
    video_path: Path | None
    Retorna o resultado principal (pode ser None).
    """
    print("\\n🎯  MINHA SKILL\\n")
    # ... lógica aqui
    return resultado
```

## Skills Existentes

| Módulo | Função principal | Retorno |
|---|---|---|
| `main.skill_download_youtube` | Download de vídeo | `Path` |
| `main.skill_detectar_virais` | Detecção viral | `list[dict]` |
| `main.skill_gerar_legendas` | Geração de `.srt` | `Path` |
| `main.skill_reframe_916` | Reformatação 9:16 | `None` |

## Adicionando uma Nova Skill ao Menu

Em `main.py`, adicione no `MENU_PRINCIPAL` e no loop `while True`:

```python
elif opcao == "7":
    from skills.minha_skill import run as minha_skill
    minha_skill(video_path=ultimo_video)
```

## Convenções

- Use as constantes de cor (`GR`, `YL`, `RD`, `CY`, `MG`, `DM`, `B`, `R`) para manter o visual consistente
- Sempre salve outputs em `OUTPUT_DIR`
- Use `TEMP_DIR` para arquivos temporários
- Nomes de arquivo de saída: `{video_stem}_descricao.ext`
