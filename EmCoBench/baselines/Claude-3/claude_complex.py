import anthropic
import base64
import json
import argparse
import time
from tqdm import tqdm

def write_to_json(obj_dict, json_file_path):
    with open(json_file_path, 'a') as json_file:
        json_file.write(json.dumps(obj_dict) + '\n')

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def ask_claude(prompt, image_path, model="claude-3-haiku-20240307", media_type="image/jpeg", max_tokens=512):
    # image1_media_type = "image/jpeg" # Claude currently support JPEG, PNG, GIF, and WebP image formats, specifically image/jpeg, image/png, image/gif, and image/webp.
    client = anthropic.Anthropic(api_key="YOUR_API_KEY")
    image_data = encode_image(image_path)
    while True:
        try:
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            return message.content[0].text
        except Exception as e:
            print(e)
            time.sleep(0.1)

def main(gt_file, output_file, image_path):   
    with open(gt_file) as f:
        data_json = []
        for line in f:
            data_json.append(json.loads(line))

    for datas in tqdm(data_json):
        for img_path, data in datas.items():
            for question, gt in data.items():
                content = f"You are a good expert of emotion understanding. Look at the image, {question}"
                output = ask_claude(prompt=content, image_path=image_path+img_path, model="claude-3-sonnet-20240229")
                write_to_json({f"{img_path}": output}, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Emotional Understanding Records.")
    parser.add_argument("--gt-file", type=str, help="Path to ground truth data file (JSON).", default="ec_comlex.jsonl")
    parser.add_argument("--output-file", type=str, help="Path to output JSONL file.")
    parser.add_argument("--image-path", type=str, help="Path to dataset.")
    args = parser.parse_args()

    main(args.gt_file, args.output_file, args.image_path)
