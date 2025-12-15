import requests


class ImagesApi:
    def get_image_src(self, image_url: str):
        try:
            res = requests.get(image_url)
            if res.status_code != 200:
                return None

            content_type = res.headers.get("Content-Type", "").lower()
            if "svg" in content_type:
                src = res.text
            else:
                src = res.content

            return src

        except Exception as e:
            print(e)
            return None