# AI UPDATE production

The only active instruction file is [production-brief.txt](production-brief.txt). It contains the current show scope, research method, scene requirements and delivery criteria.

`generate_episode.py generate --episode ID` produces a dated pending plan from that brief. It performs no research, tests, narration or rendering. Existing episode folders are never overwritten. `--duration-seconds` and `--scope` record a later explicit request; they do not replace the master rules. The default current request is the 60-second introduction.

Other formerly active instruction filenames are compatibility redirects. Their original bytes are retained under [history/pre-clean-slate-2026-10-13](history/pre-clean-slate-2026-10-13). Existing episodes remain historical and unchanged.
