import requests


class MashiApi:
    def get_mashi_data(self, wallet: str) -> dict:
        try:
            res = requests.get(f"https://mash-it.io/api/mashers/latest?wallet={wallet}")
            data = res.json()
            if data.get("message") == "No mashups found":
                return {}

            colors = data.get("colors", {})
            traits = data.get("assets", [])

            return {
                "colors": colors,
                "assets": traits
            }

        except Exception as e:
            print(e)
            return {}


    def simulate_mashi_data(self) -> dict:
        colors = {
            "base":"#E4CABE",
            "eyes":"#0EAAED",
            "hair":"#E24712"
        }
        traits = [
            {"name":"background","image":"https://ipfs.io/ipfs/QmWCqFphy8GEPr5GowgmQZTucfmB7V7efQBDZQ99C8ESxY"},
            {"name":"hair_back","image":"https://ipfs.io/ipfs/QmUqSibWsp7UF9h5XFMYfi9xJdHvHDe5rmRPUCsbP57GGX"},
            {"name":"bottom","image":"https://ipfs.io/ipfs/QmX9YYA8jAxAEroNkGHQWdmLHpiRbt26fvp1zvQFoL8YNJ"},
            {"name":"upper","image":"https://ipfs.io/ipfs/QmebU67K3a2gYve4qH7haRSNQ2PZ1CN242xivunrerDEcM"},
            {"name":"head","image":"https://ipfs.io/ipfs/QmcTeG6CSzAMKP9xp5CKfewDbTUEa5RBcvkxGeNXW3KBQi"},
            {"name":"eyes","image":"https://ipfs.io/ipfs/QmYFGZm34kNADVEf44YxihmtCgRjr1itTvuWVuSVqkTABi"},
            {"name":"hair_front","image":"https://ipfs.io/ipfs/QmUZxRsQc8z2TMmiod3mSUeRh5wespJGarRELYZV9Zbw1o"},
            {"name":"hat","image":"https://ipfs.io/ipfs/QmNZwsJVARPhy6Vs9jRzxjt9t5HWH3Bf5kuAGxTQ3kZBS9"},
            {"name":"left_accessory","image":"https://ipfs.io/ipfs/QmUYr95SvARnDXrMgTF3dUo98Z1p91LEnqGMBNcfaXB4FU"},
            {"name":"right_accessory","image":"https://ipfs.io/ipfs/QmanMmH6SqCo8WH7VaUDrauXsu6HXkiQWVQ7RQafgmujom"}
        ]

        return {
            "colors": colors,
            "assets": traits
        }