# Fixed messages

Interface text, not prose: these messages are delivered verbatim, never paraphrased. Only the English templates ship; at use time they are translated faithfully into the conversation's language — minding that language's own sentence order and idiom, because a fixed message badly translated is worse than none. `{placeholders}` are resolved at delivery time.

## Plan-mode notice

Opens the first reply whenever the session is in plan mode and the requested work writes files:

> NOTICE: this session is running in plan mode, and working on a space requires an action mode (manual approval, accept edits, or automatic). To switch modes: shift+tab in the terminal; in the desktop app, click the mode selector next to the send button; on the web, the mode dropdown next to the prompt box. Once you have switched modes, we’ll continue.

## Plan-mode exit plan

The plan text passed to the exit mechanism; no design vocabulary, no skill or agent names:

> **Set up the collaboration space**
>
> I will ask you only the essentials and, with your answers, create the space’s folder with everything it needs to work: its records, its configuration, and its map. Nothing outside that folder will be touched, and nothing will be created before you have confirmed the key details.

## Post-creation notice

Delivered immediately after creation completes on validator green:

> Your space is created and working — every check passed. A few things would make it more useful whenever you have them: {useful-data}. You can give me any of them now or at any later moment; nothing is blocked in the meantime.

`{useful-data}` is derived at delivery time from what the space's seeded schemas and registered skills can use — named in plain language, never as field names.
