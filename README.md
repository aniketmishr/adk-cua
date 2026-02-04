# Computer Use Agent

# Demo
> Agent Opens Youtube Video from a playlist of Andrej Karpathy 

https://github.com/user-attachments/assets/e5dabc81-ffac-4c12-bd7c-db7dbbb96dfb

> Agent uploads a reel to instagram account of user

https://github.com/user-attachments/assets/7f931bda-307b-47da-ae9f-4658ea55933f

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

