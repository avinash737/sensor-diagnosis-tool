import subprocess
import asyncio
import websockets
from multiprocessing import Process, Queue
from FeetPlotter import *


def compileJavaProgramm(pathToScript):
    try:
        subprocess.run(pathToScript, shell=True, check=True)
        subprocess.CompletedProcess(args=pathToScript, returncode=0)
        return True
    except Exception as err:
        print(err)
        return False


def run_java_program(path: str, foldername: str):
    os.environ['CONFIG_PATH'] = join('/home/jonathan/Documents/Incoretex/deichmann/Reanalysis', 'local_config.json')
    PRG_NAME = join('/home/jonathan/Documents/Incoretex/deichmann/Reanalysis', 'exe', 'jdruckdirk.jar ')
    OPT: Final = ' --batchAnalysis --debugOutput --iterOutput --fromRaw --reanalysis --mirrorVirtualFeet --streamlined --path '
    command = ['java -Xss32m -Xms512m -Xmx1024m -jar ' + str(PRG_NAME) + OPT + path + foldername]
    try:
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        subprocess.CompletedProcess(args=command, returncode=0)
        return True,
    except Exception as err:
        print(err)
        return False


def handleFailed(original, resultFolder, name):
    try:
        os.makedirs(join(resultFolder, "00_Failed"))
    except:
        pass
    shutil.copytree(join(original, name), join(resultFolder, "00_Failed", name))


async def handler(websocket):
    global sucQueue, failQueue, server
    while True:
        message = await websocket.recv()
        print(message)
        jsonData = json.loads(message)
        if jsonData["method"] == "succ":
            sucQueue.put(jsonData["data"])
        if jsonData["method"] == "failed":
            failQueue.put(jsonData["data"])
        if jsonData["method"] == "done":
            sucQueue.put(None)
            failQueue.put(None)
            asyncio.Future().set_result("done")


async def startServer():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


def plotter(queue):
    while True:
        item = queue.get()
        if item is not None:
            plotFeetAllCurrentFeatures("/".join(item.split("/")[:-1]), item.split("/")[-1])
            print("{} To create".format(queue.qsize()), sep="\r")
        else:
            break


def failHandler(queue):
    global path
    while True:
        item = queue.get()
        if item is not None:
            handleFailed(path, "/".join(item.split("/")[:-1]), item.split("/")[-1])
        else:
            break


if __name__ == '__main__':
    pathToCompileScript = r"bash /home/jonathan/Documents/Incoretex/deichmann/jdruckdirk/compileForLinuxCopy"
    path = r"/home/jonathan/Documents/Incoretex/deichmann/Reanalysis/kindergartenAll/"
    if compileJavaProgramm(pathToCompileScript):
        folder = r""
        sucQueue = Queue()
        failQueue = Queue()

        plotter1 = Process(target=plotter, args=(sucQueue,))
        plotter2 = Process(target=plotter, args=(sucQueue,))
        plotter3 = Process(target=plotter, args=(sucQueue,))
        fail1 = Process(target=failHandler, args=(failQueue,))

        plotter1.start()
        plotter2.start()
        plotter3.start()
        fail1.start()
        # server = Process(target=startServer)
        # server.start()

        java = Process(target=run_java_program, args=(path, folder))
        java.start()
        asyncio.run(startServer())

        plotter1.join()
        plotter2.join()
        plotter3.join()
        fail1.join()
        # server.join()
        java.join()
        print("behind")
    else:
        print("Fix your shit ")
