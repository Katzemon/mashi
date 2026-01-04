import requests

from configs.config import ALCHEMY_API_KEY


class AlchemyApi:
    def _build_req(self, wallet: str, key: str | None = None):
        return (
                f"https://polygon-mainnet.g.alchemy.com/nft/v3/{ALCHEMY_API_KEY}/getNFTsForOwner"
                + f"?owner={wallet}"
                + "&withMetadata=true"
                + "&contractAddresses%5B%5D=0x6d74e823E3cFB94A4a395b74B1E7B0F5Ca5596A3"
                + (f"&pageKey={key}" if key else "")
        )


    def get_available_mints(self, wallet: str, background_uri: str) -> list:
        try:
            background_uri = background_uri.replace("https://ipfs.io/ipfs/", "ipfs://")
            names = []
            key = None

            while True:
                req = self._build_req(wallet, key)
                res = requests.get(req)
                if res.status_code != 200:
                    return []

                data = res.json()
                if len(data.get("ownedNfts", [])) == 0:
                    return []

                #
                nft_names = [
                    nft["name"]
                    for nft in data["ownedNfts"]
                    if any(
                        asset.get("label") == "background" and asset.get("uri") == background_uri
                        for asset in nft.get("raw", {}).get("metadata", {}).get("assets", [])
                    )
                ]
                names.extend(nft_names)

                key = data.get("pageKey")
                if not key:
                    return names

        except Exception as e:
            print(e)
            return []
