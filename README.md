# 🎬 ClipAI — Agente de IA para Criadores de Conteúdo

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/diegolandim99/chatvideos/blob/main/ClipAI.ipynb)

O **ClipAI** é um agente de Inteligência Artificial que roda gratuitamente no Google Colab, projetado para automatizar a criação de cortes virais para YouTube Shorts, TikTok e Instagram Reels — direto de qualquer vídeo do YouTube.

---

## 🚀 Como Executar (Sem Instalação)

1. Clique no badge **Abrir no Colab** acima
2. No menu superior: **Ambiente de execução → Executar tudo** (`Ctrl+F9`)
3. Aguarde ~3 minutos enquanto as dependências são instaladas
4. Clique em **🚀 ABRIR O CLIPAI** ao final

---

## 📐 Skills do Agente

| Skill | Ferramenta | O que faz |
|---|---|---|
| 🎬 Download YouTube | `yt-dlp` | Baixa em máxima qualidade (MP4) |
| ✂️ Detecção Viral | `Whisper` + `SentenceTransformers` | Transcreve e seleciona momentos virais via IA semântica |
| 📝 Legendas / CC | `Whisper` + `srt` | Gera `.srt` e opcionalmente queima no vídeo |
| 📱 Reframe 9:16 | `ffmpeg` | Recorta e converte para formato TikTok/Reels |

---

## 🏗️ Arquitetura
