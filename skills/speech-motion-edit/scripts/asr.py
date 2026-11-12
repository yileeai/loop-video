import sys, json
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = m.transcribe(sys.argv[1], language="zh", word_timestamps=True, initial_prompt="以下是普通话口播，关于AI。")
out=[]
for s in segs:
    out.append({"start":round(s.start,2),"end":round(s.end,2),"text":s.text,"words":[[round(w.start,2),round(w.end,2),w.word] for w in s.words]})
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}")
json.dump(out, open(sys.argv[2],"w",encoding="utf-8"), ensure_ascii=False, indent=1)
