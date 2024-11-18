import os
import asyncio
import aiohttp
import subprocess


async def download_ts_file(session, url, file_path, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(file_path, 'wb') as file:
                        file.write(content)
                    print(f"Downloaded {url} to {file_path}")
                    return file_path
                else:
                    print(f"Failed to download {url}, status code: {response.status}")
        except aiohttp.ClientPayloadError as e:
            print(f"ClientPayloadError on {url}: {e}, retrying ({attempt + 1}/{retries})")
        except Exception as e:
            print(f"Unexpected error on {url}: {e}, retrying ({attempt + 1}/{retries})")

    print(f"Failed to download {url} after {retries} attempts")
    return None


async def download_ts_files(base_url, start_number, end_number, save_folder):
    # Make sure that the filepath exists.
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    tasks = []
    ts_files_list = []

    async with aiohttp.ClientSession() as session:
        for i in range(start_number, end_number + 1):
            url = f"{base_url}{i}.ts"
            file_path = os.path.join(save_folder, f"{i}.ts")
            task = asyncio.create_task(download_ts_file(session, url, file_path))
            tasks.append(task)

        completed_tasks = await asyncio.gather(*tasks)
        for task in completed_tasks:
            if task is not None:
                ts_files_list.append(task)

    return ts_files_list


def create_file_list(ts_files_list, file_list_path):
    with open(file_list_path, 'w') as file:
        for ts_file in ts_files_list:
            file.write(f"file '{os.path.abspath(ts_file)}'\n")


# Set the information about the https.
base_url = "https://dh5.cntv.myalicdn.com/asp/h5e/hls/2000/0303000a/3/default/dc1478da562844a6b3e77d86aceafe6b/"
start_number = 1
end_number = 150
save_folder = r""
output_mp4_path = r""


async def main():
    ts_files_list = await download_ts_files(base_url, start_number, end_number, save_folder)
    file_list_path = os.path.join(save_folder, "file_list.txt")
    create_file_list(ts_files_list, file_list_path)


# 运行主函数
asyncio.run(main())