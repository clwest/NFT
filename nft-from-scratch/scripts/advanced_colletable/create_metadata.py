from brownie import AdvancedCollectible, network
from scripts.helpful_scripts import get_breed
from metadata import sample_metadata
from pathlib import Path
import os
import requests
import json

def main():
    print("Working on " + network.show_active())
    advanced_collectible = AdvancedCollectible[len(AdvancedCollectible) - 1]
    number_of_tokens = advanced_collectible.tokenCounter()
    print("The number of tokens you have deployed is {}".format(number_of_tokens))
    write_metadata(number_of_tokens, advanced_collectible)

def write_metadata(number_of_tokens, nft_contract):
    for token_id in range(number_of_tokens):
        collectable_metadata = sample_metadata.metadata_template
        breed = get_breed(nft_contract.tokenIdToBreed(token_id))
        metadata_file_name = (
            "./metadata/{}/".format(network.show_active()) + str(token_id) + "-" + breed + ".json")
        if Path(metadata_file_name).exists():
            print("{} already found!".format(metadata_file_name))
        else:
            print("Creating Metadata File {}".format(metadata_file_name))
            collectable_metadata["name"] = get_breed(nft_contract.tokenIdToBreed(token_id))
            collectable_metadata["description"] = "An adorable {} pup!".format(collectable_metadata["name"])
            image_to_upload = None
            if os.getenv("UPLOAD_IPFS") == "true":
                image_path = "./img/{}.png".format(breed.lower().replace("_", "-"))
                image_to_upload = upload_to_ipfs(image_path)
            collectable_metadata["image"] = image_to_upload
            with open(metadata_file_name, "w") as file:
                json.dump(collectable_metadata, file)
            if os.getenv("UPLOAD_IPFS") == "true":
                upload_to_ipfs(metadata_file_name)

                
# 0xf4ada3c691f787583696cff58b903b853e00ecf07f1fee8d81efb09666270e5c



def upload_to_ipfs(filepath):
    with Path(filepath).open("rb") as fp:
        image_binary = fp.read()
        ipfs_url = "http://localhost:5001"
        response = requests.post(ipfs_url + "/api/v0/add", files={"file": image_binary})
        ipfs_hash = response.json()["Hash"]
        filename = filepath.split("/")[-1:][0]
        uri = "https://ifps.io/ipfs/{}?filename={}".format(
            ipfs_hash, filename
        )
        print(uri)
        return uri
    return None