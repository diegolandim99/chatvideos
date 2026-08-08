"""
ClipAI — Agente de IA para Criadores de Conteúdo
Gera cortes virais para YouTube, TikTok e Reels automaticamente.
"""

import os
import sys
import subprocess
import shutil
import textwrap
from pathlib import Path

# ── Paleta de cores ANSI ────────────────────────────────────────────────────
R  = "\033[0m"       # reset
B  = "\033[1m"       # bold
CY = "\033[96m"      # ciano
YL = "\033[93m"      # amarelo
GR = "\033[92m"      # verde
RD = "\033[91m"      # vermelho
MG = "\033[95m"      # magenta
DM = "\033[2m"       # dim

BANNER = f"""
{CY}{B}
 ██████╗██╗     ██╗██████╗      █████╗ ██╗
██╔════╝██║     ██║██╔══██╗    ██╔══██╗██║
██║     ██║     ██║██████╔╝    ███████║██║
██║     ██║     ██║██╔═══╝     ██╔══██║██║
╚██████╗███████╗██║██║         ██║  ██║██║
 ╚═════╝╚══════╝╚═╝╚═╝         ╚═╝  ╚═╝╚═╝
{R}{MG}{B}   Agente de IA para Criadores de Conteúdo   {R}
{DM}   YouTube Shorts · TikTok · Instagram Reels  {R}
"""

MENU_PRINCIPAL = f"""
{B}{CY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}
{B}  MENU PRINCIPAL{R}
{CY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}

  {GR}{B}[1]{R}  🎬  Processar vídeo do YouTube
  {GR}{B}[2]{R}  ✂️   Detectar momentos virais (IA)
  {GR}{B}[3]{R}  📝  Gerar legendas / closed caption
  {GR}{B}[4]{R}  📱  Reformatar para 9:16 (TikTok/Reels)
  {GR}{B}[5]{R}  🚀  Pipeline completo (tudo em sequência)
  {YL}{B}[6]{R}  ⚙️   Configurações
  {RD}{B}[0]{R}  ❌  Sair

{CY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R}
"""

OUTPUT_DIR = Path("/content/drive/MyDrive/ClipAI") if Path("/content").exists() else Path.home() / "ClipAI"
TEMP_DIR   = Path("/tmp/clipai_work")


def garantir_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def cmd(command: list, desc: str = "") -> subprocess.CompletedProcess:
    if desc:
        print(f"{DM}  › {desc}...{R}")
    return subprocess.run(command, capture_output=True, text=True)


def checar_deps() -> bool:
    """Verifica e instala dependências em tempo de execução."""
    deps = {
        "yt-dlp":      ["pip", "install", "-q", "yt-dlp"],
        "ffmpeg":      None,  # já vem no Colab
        "whisper":     ["pip", "install", "-q", "openai-whisper"],
        "transformers":["pip", "install", "-q", "transformers", "torch"],
        "srt":         ["pip", "install", "-q", "srt"],
    }
    print(f"\n{CY}  Verificando dependências...{R}")
    for lib, install_cmd in deps.items():
        try:
            __import__(lib.replace("-", "_"))
            print(f"  {GR}✔{R}  {lib}")
        except ImportError:
            if install_cmd:
                print(f"  {YL}⬇{R}  Instalando {lib}...")
                cmd(install_cmd)
                print(f"  {GR}✔{R}  {lib} instalado")
            else:
                print(f"  {YL}⚠{R}  {lib} (sistema)")
    return True


# ── Skill 1 · Download YouTube ──────────────────────────────────────────────
def skill_download_youtube():
    print(f"\n{CY}{B}🎬  DOWNLOAD DO YOUTUBE{R}\n")
    url = input(f"  {YL}URL do vídeo:{R} ").strip()
    if not url:
        print(f"  {RD}URL não informada.{R}")
        return None

    out_path = TEMP_DIR / "%(title)s.%(ext)s"
    print(f"\n  {DM}Baixando...{R}")
    result = subprocess.run(
        ["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
         "--merge-output-format", "mp4",
         "-o", str(out_path), url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  {RD}Erro no download:{R}\n{result.stderr[:300]}")
        return None

    # Descobre o arquivo gerado
    arquivos = sorted(TEMP_DIR.glob("*.mp4"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not arquivos:
        print(f"  {RD}Arquivo não encontrado após download.{R}")
        return None

    video_path = arquivos[0]
    print(f"\n  {GR}✔  Vídeo salvo em:{R} {video_path.name}")
    return video_path


# ── Skill 2 · Detecção de Momentos Virais ───────────────────────────────────
def skill_detectar_virais(video_path: Path):
    """
    Usa Whisper para transcrever e um modelo de linguagem leve
    para pontuar os segmentos com maior potencial viral.
    """
    print(f"\n{MG}{B}✂️  DETECÇÃO DE MOMENTOS VIRAIS{R}\n")
    print(f"  {DM}Transcrevendo áudio com Whisper (modelo 'small')...{R}")

    import whisper
    model = whisper.load_model("small")
    result = model.transcribe(str(video_path), language="pt", verbose=False)

    segments = result.get("segments", [])
    if not segments:
        print(f"  {RD}Nenhum segmento encontrado.{R}")
        return []

    print(f"  {GR}✔  {len(segments)} segmentos transcritos.{R}")
    print(f"\n  {CY}Analisando potencial viral com IA...{R}")

    # Palavras-chave de alto engajamento (heurística + expansível via LLM)
    GATILHOS = [
        "segredo","revelação","nunca contei","surpreendente","inacreditável",
        "erro","falha","aconteceu","mudou tudo","viralizou","polêmica",
        "verdade","confissão","exclusivo","impressionante","incrível",
        "finalmente","atualização","urgente","importante","descoberta",
        "react","reagindo","chocante","absurdo","estratégia",
    ]

    clips_pontuados = []
    for seg in segments:
        texto = seg["text"].lower()
        score = sum(2 for g in GATILHOS if g in texto)
        # Bônus por duração ideal (20-60s)
        duracao = seg["end"] - seg["start"]
        if 20 <= duracao <= 60:
            score += 3
        elif duracao < 10:
            score -= 2
        clips_pontuados.append({
            "start":  seg["start"],
            "end":    seg["end"],
            "texto":  seg["text"].strip(),
            "score":  score,
        })

    # Top clips (score > 0, máx 10)
    top = sorted([c for c in clips_pontuados if c["score"] > 0],
                 key=lambda x: x["score"], reverse=True)[:10]

    if not top:
        print(f"  {YL}Nenhum momento viral detectado. Exibindo todos os segmentos.{R}")
        top = clips_pontuados[:5]

    print(f"\n  {GR}{B}TOP MOMENTOS VIRAIS:{R}\n")
    for i, clip in enumerate(top, 1):
        inicio = _fmt_tempo(clip["start"])
        fim    = _fmt_tempo(clip["end"])
        print(f"  {CY}[{i:02d}]{R} {inicio} → {fim}  {YL}⭐ score {clip['score']}{R}")
        print(f"       {DM}{clip['texto'][:80]}...{R}\n")

    # Salvar JSON dos clips
    import json
    json_path = OUTPUT_DIR / f"{video_path.stem}_clips.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(top, f, ensure_ascii=False, indent=2)
    print(f"  {GR}✔  Clips salvos em:{R} {json_path}")
    return top


# ── Skill 3 · Legendas / Closed Caption ────────────────────────────────────
def skill_gerar_legendas(video_path: Path):
    print(f"\n{YL}{B}📝  GERAÇÃO DE LEGENDAS{R}\n")
    print(f"  {DM}Transcrevendo com Whisper...{R}")

    import whisper, srt, datetime
    model = whisper.load_model("small")
    result = model.transcribe(str(video_path), language="pt",
                               word_timestamps=True, verbose=False)

    subs = []
    for i, seg in enumerate(result["segments"], 1):
        subs.append(srt.Subtitle(
            index=i,
            start=datetime.timedelta(seconds=seg["start"]),
            end=datetime.timedelta(seconds=seg["end"]),
            content=seg["text"].strip()
        ))

    srt_path = OUTPUT_DIR / f"{video_path.stem}.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(subs))

    print(f"  {GR}✔  {len(subs)} legendas geradas.{R}")
    print(f"  {GR}✔  Arquivo SRT:{R} {srt_path}")

    # Queimar legenda no vídeo (opcional)
    resp = input(f"\n  {YL}Queimar legenda no vídeo? (s/n):{R} ").strip().lower()
    if resp == "s":
        saida = OUTPUT_DIR / f"{video_path.stem}_legendado.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(video_path),
            "-vf", f"subtitles={srt_path}:force_style='FontName=Arial,FontSize=18,"
                   f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,"
                   f"Alignment=2'",
            "-c:a", "copy", str(saida)
        ], capture_output=True)
        print(f"  {GR}✔  Vídeo legendado:{R} {saida.name}")
    return srt_path


# ── Skill 4 · Reformatar 9:16 ───────────────────────────────────────────────
def skill_reframe_916(video_path: Path, clips: list = None):
    print(f"\n{GR}{B}📱  REFORMATAR PARA 9:16 (TikTok/Reels){R}\n")

    if not clips:
        # Modo manual: usuário informa início e fim
        print(f"  {DM}Informe o trecho para recortar (ou Enter para o vídeo inteiro):{R}")
        inicio_str = input(f"  {YL}Início (ex: 00:01:30):{R} ").strip() or "0"
        fim_str    = input(f"  {YL}Fim    (ex: 00:02:00):{R} ").strip() or ""
        clips_a_processar = [{"start": _parse_tempo(inicio_str),
                               "end":   _parse_tempo(fim_str) if fim_str else None,
                               "texto": "clip_manual"}]
    else:
        # Usar clips detectados pela IA
        print(f"  Processando {len(clips)} clips detectados pela IA...\n")
        clips_a_processar = clips

    for i, clip in enumerate(clips_a_processar, 1):
        inicio = clip["start"]
        fim    = clip.get("end")
        nome   = f"{video_path.stem}_clip{i:02d}_916.mp4"
        saida  = OUTPUT_DIR / nome

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-ss", str(inicio),
        ]
        if fim:
            ffmpeg_cmd += ["-to", str(fim)]
        ffmpeg_cmd += [
            "-i", str(video_path),
            # Crop central + escala para 1080x1920
            "-vf", "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            str(saida)
        ]

        print(f"  {CY}[{i:02d}]{R} Exportando {nome}...")
        r = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        if r.returncode == 0:
            print(f"       {GR}✔  Salvo em:{R} {saida}")
        else:
            print(f"       {RD}✗  Erro:{R} {r.stderr[:200]}")

    print(f"\n  {GR}✔  Clips exportados para:{R} {OUTPUT_DIR}")


# ── Pipeline Completo ────────────────────────────────────────────────────────
def pipeline_completo():
    print(f"\n{MG}{B}🚀  PIPELINE COMPLETO{R}")
    print(f"  {DM}Download → Virais → Legendas → 9:16{R}\n")

    video = skill_download_youtube()
    if not video:
        return

    clips = skill_detectar_virais(video)
    skill_gerar_legendas(video)
    skill_reframe_916(video, clips)

    print(f"\n{GR}{B}  ✅  Pipeline concluído!{R}")
    print(f"  Todos os arquivos em: {GR}{OUTPUT_DIR}{R}\n")


# ── Configurações ────────────────────────────────────────────────────────────
def menu_configuracoes():
    print(f"\n{YL}{B}⚙️  CONFIGURAÇÕES{R}\n")
    print(f"  {CY}Pasta de saída atual:{R} {OUTPUT_DIR}")
    print(f"  {CY}Pasta temporária:{R}    {TEMP_DIR}")
    print(f"\n  {DM}[Em breve: modelo Whisper, idioma, resolução de saída...]{R}\n")
    input(f"  {YL}Enter para voltar...{R}")


# ── Helpers ──────────────────────────────────────────────────────────────────
def _fmt_tempo(segundos: float) -> str:
    m, s = divmod(int(segundos), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _parse_tempo(s: str) -> float:
    partes = s.strip().split(":")
    try:
        if len(partes) == 3:
            return int(partes[0])*3600 + int(partes[1])*60 + float(partes[2])
        elif len(partes) == 2:
            return int(partes[0])*60 + float(partes[1])
        else:
            return float(partes[0])
    except ValueError:
        return 0.0


# ── Loop principal ────────────────────────────────────────────────────────────
def run():
    garantir_dirs()
    os.system("clear")
    print(BANNER)
    checar_deps()

    while True:
        print(MENU_PRINCIPAL)
        opcao = input(f"  {YL}{B}Escolha uma opção:{R} ").strip()

        if opcao == "1":
            skill_download_youtube()
        elif opcao == "2":
            arquivos = sorted(TEMP_DIR.glob("*.mp4"))
            if not arquivos:
                print(f"\n  {RD}Nenhum vídeo baixado ainda. Use a opção [1] primeiro.{R}\n")
            else:
                print(f"\n  {CY}Vídeos disponíveis:{R}")
                for i, f in enumerate(arquivos, 1):
                    print(f"  [{i}] {f.name}")
                idx = input(f"  {YL}Escolha o número:{R} ").strip()
                try:
                    skill_detectar_virais(arquivos[int(idx)-1])
                except (IndexError, ValueError):
                    print(f"  {RD}Opção inválida.{R}")
        elif opcao == "3":
            arquivos = sorted(TEMP_DIR.glob("*.mp4"))
            if not arquivos:
                print(f"\n  {RD}Nenhum vídeo baixado ainda. Use a opção [1] primeiro.{R}\n")
            else:
                skill_gerar_legendas(arquivos[-1])
        elif opcao == "4":
            arquivos = sorted(TEMP_DIR.glob("*.mp4"))
            if not arquivos:
                print(f"\n  {RD}Nenhum vídeo baixado ainda. Use a opção [1] primeiro.{R}\n")
            else:
                skill_reframe_916(arquivos[-1])
        elif opcao == "5":
            pipeline_completo()
        elif opcao == "6":
            menu_configuracoes()
        elif opcao == "0":
            print(f"\n  {CY}Até logo! ✌️{R}\n")
            sys.exit(0)
        else:
            print(f"\n  {RD}Opção inválida.{R}\n")


if __name__ == "__main__":
    run()
