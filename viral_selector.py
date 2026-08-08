"""Seleção de cortes virais local, sem API paga."""

MIN_CLIP_SECONDS = 30
MAX_CLIP_SECONDS = 60
TARGET_CLIP_SECONDS = 45
MAX_CLIPS = 8
MIN_SCORE = 0.38
MIN_GAP_SECONDS = 8

CONCEPTS = [
    "um gancho forte que desperta curiosidade imediatamente",
    "uma revelação ou descoberta surpreendente",
    "uma afirmação polêmica ou opinião forte",
    "uma história pessoal com emoção ou conflito",
    "uma explicação útil que resolve um problema",
    "uma dica prática que o público pode aplicar",
    "um erro comum e como evitá-lo",
    "uma mudança de perspectiva ou insight importante",
    "um momento engraçado, absurdo ou inesperado",
    "uma frase forte que funciona como abertura de vídeo curto",
]

GATILHOS = [
    "segredo", "revelação", "nunca contei", "surpreendente", "inacreditável",
    "erro", "falha", "aconteceu", "mudou tudo", "viralizou", "polêmica",
    "verdade", "confissão", "exclusivo", "impressionante", "incrível",
    "finalmente", "atualização", "urgente", "importante", "descoberta",
    "chocante", "absurdo", "estratégia", "problema", "como fazer", "dica",
    "aprendi", "não faça", "o que ninguém", "atenção", "cuidado",
]


def _fallback(texts):
    out=[]
    for text in texts:
        low=text.lower()
        hits=sum(1 for g in GATILHOS if g in low)
        density=min(1.0, len(low.split())/90.0)
        out.append(0.75*min(1.0,hits/4.0)+0.25*density)
    return out


def _windows(segments):
    out=[]
    seen=set()
    for i, seg in enumerate(segments):
        start=float(seg["start"]); end=start; parts=[]
        for j in range(i, len(segments)):
            end=float(segments[j]["end"])
            parts.append(segments[j]["text"].strip())
            if end-start >= TARGET_CLIP_SECONDS or end-start >= MAX_CLIP_SECONDS:
                break
        dur=end-start
        if MIN_CLIP_SECONDS <= dur <= MAX_CLIP_SECONDS:
            key=(round(start,1),round(end,1))
            if key not in seen:
                seen.add(key); out.append({"start":start,"end":end,"texto":" ".join(parts)})
    return out


def _semantic(texts):
    try:
        from sentence_transformers import SentenceTransformer, util
        model=SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        emb=model.encode(texts,batch_size=16,show_progress_bar=False,normalize_embeddings=True)
        concepts=model.encode(CONCEPTS,batch_size=16,show_progress_bar=False,normalize_embeddings=True)
        sim=util.cos_sim(emb,concepts).max(dim=1).values.cpu().tolist()
        return [float(max(0,min(1,x))) for x in sim], True
    except Exception as exc:
        print(f"  ⚠ IA semântica indisponível; usando fallback local: {str(exc)[:160]}")
        return _fallback(texts), False


def _select(candidates):
    chosen=[]
    for c in sorted(candidates,key=lambda x:x["score"],reverse=True):
        conflict=False
        for x in chosen:
            overlap=c["start"] < x["end"] and c["end"] > x["start"]
            close=abs(c["start"]-x["end"]) < MIN_GAP_SECONDS or abs(x["start"]-c["end"]) < MIN_GAP_SECONDS
            if overlap or close:
                conflict=True; break
        if not conflict:
            chosen.append(c)
        if len(chosen)>=MAX_CLIPS: break
    return sorted(chosen,key=lambda x:x["start"])


def select_viral_clips(segments):
    candidates=_windows(segments)
    if not candidates: return [], False
    texts=[c["texto"] for c in candidates]
    semantic, used_ai=_semantic(texts)
    for c,s in zip(candidates,semantic):
        dur=c["end"]-c["start"]
        duration_score=max(0.0,1.0-abs(dur-TARGET_CLIP_SECONDS)/TARGET_CLIP_SECONDS)
        density=min(1.0,len(c["texto"].split())/90.0)
        c["score"]=round(0.70*s+0.20*duration_score+0.10*density,4)
        c["semantic_score"]=round(s,4)
        c["duracao"]=round(dur,2)
    approved=[c for c in candidates if c["score"]>=MIN_SCORE]
    if len(approved)<3:
        approved=sorted(candidates,key=lambda x:x["score"],reverse=True)[:max(3,MAX_CLIPS)]
    return _select(approved), used_ai
