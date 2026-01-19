# Computer Use Agent

[Watch the demo video - YouTube Search](https://youtu.be/1FbDgAi7uB8)

[![Watch the video](https://img.youtube.com/vi/1FbDgAi7uB8/hqdefault.jpg)](https://www.youtube.com/watch?v=1FbDgAi7uB8)


Setup instruction: 
create new file `.env` in folder `cua/` refer `cua/.env.example` paste your API key's
```
python -m venv .venv
.venv/Scripts/activate  # for windows

pip install -r requirements.txt
```

To run agent (from root of the project):
1. First start omni server
    `python -m omni.server`
2. Run cli
    `python cli.py`

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

It includes code from the `trycua/cua/som` project, which is also licensed under AGPL-3.0.
The included `trycua/cua/som` source code has been modified for use in this project.

