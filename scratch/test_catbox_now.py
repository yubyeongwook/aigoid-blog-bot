import requests
image_path = r"c:\Users\aigoi\OneDrive\바탕 화면\안티 프로젝트\BLOG_AUTO\aigoid-blog-bot\assets\brand_banner.png"
url = "https://catbox.moe/user/api.php"
data = {"reqtype": "fileupload"}
files = {"fileToUpload": open(image_path, "rb")}
res = requests.post(url, data=data, files=files)
print(res.status_code, res.text)
