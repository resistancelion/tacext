import io, re, sys, os, shutil, subprocess, pathlib, json, itertools, urllib.request, xml.etree.ElementTree as ET
from frozendict import frozendict as fd
from colorama import init, Fore as FG, Style as ST

STA = ST.RESET_ALL
FGR = FG.RED
FGG = FG.GREEN

OFFICIAL_LIST = [ [1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [2040], [2496] ]
SUPP_EXTS = fd({"apk": "apk", "apkm": "apk", "aab": "apk", "akp": "apk"})
# xapk/apkx, apks, exe - not ready!

validconf = fd({"yes": True, "y": True, "ye": True, "no": False, "n": False, "ні": False, "так": True, "нє": False, "та": True, "н": False, "т": True})
validconfall = fd({"ту":True, "ну":False, "тєу":True, "нєу":False, "усе":True, "ніт":False, "усє":True, "усьо":True, "вт":True, "вн":False, "тв":True, "нв":False, "ут":True, "ун":False, "ys":True, "ns":False, "ya":True, "na":False, "ay":True, "an":False, "all":True, "йєп":True, "ноуп":False})
yes_to_all = False
no_to_all = False
logm = True

def wposs(v):
    return isinstance(v, io.IOBase) and hasattr(v, 'write') and not v.closed
    
def wu(content):
    global foutJSON
    if toCons:
        sys.stdout.write(content)
    
    if wposs(foutJSON):
        foutJSON.write(content)
        
def err(t,v):
    if not toCons:
        raise [RuntimeError, ValueError, TypeError][t](f"{FGR}[ХИБА] {v}{STA}")
    
def log(v):
    if logm:
        print(f"{FG.YELLOW}[ЗВІТ] {v}{STA}")
    

def cnfrm(question, default="ні"):
    if yes_to_all:
        return True
    if no_to_all:
        return False
    
    if default is None:
        prompt = " [т/н] "
    elif default in validconf and validconf[default]:
        prompt = " [Т/н] "
    elif default in validconf and not validconf[default]:
        prompt = " [т/Н] "
    else:
        err(1,f"cnfrm неправильне стандартне значення: '{default}'")

    if toCons:
        return validconf[default]

    while True:
        choice = input(f"{question}{prompt}").strip().lower()
        if default is not None and choice == "":
            return validconf[default]
        elif choice in validconf:
            return validconf[choice]
        elif choice in validconfall:
            if validconfall[choice]:
                yes_to_all = True
            else:
                no_to_all = True
            return validconfall[choice] 
        else:
            print(f"Невірна відповідь, використайте для одного разу: [" + " або ".join(validconf) + "], для завжди: ["  + " або ".join(validconfall) + "]")
            
def download_last_repo_release(owner, repo, ext, filename):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    headers = {'Accept': 'application/vnd.github.v3+json'}

    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as response:
            release_data = json.loads(response.read().decode())
    
        for asset in release_data['assets']:
            if asset['name'].endswith(ext):
                download_url = asset['browser_download_url']
                if len(filename) < 1:
                    filename = asset['name']
                log(f"Завантаження {filename} з {download_url}")
                urllib.request.urlretrieve(download_url, filename)
                break
        else:
            err(1,f"download_last_repo_release файла з розширенням {ext} не знайдено в останньому релізі '{owner}/{repo}'.")
    except Exception as e:
        err(0,f"URLlib: {e}") 
        return False
            
    return True
    
def det_OS():
    if sys.platform == "win32" or sys.platform == "win64" or sys.platform == "win" or sys.platform == "winARM" or sys.platform == "windows":
        return "windows", ".bat"
    elif sys.platform == "linux" or sys.platform == "linux2":
        return "linux", ""
    elif sys.platform == "darwin":
        return "osx", ""
    else:
        return "linux", ""

def download_tools():
    _ = download_last_repo_release("ibotpeaches", "apktool", ".jar", "apktool.jar")
    _os, ext = det_OS()
    try:
        urllib.request.urlretrieve(f"https://raw.githubusercontent.com/iBotPeaches/Apktool/refs/heads/main/scripts/{_os}/apktool{ext}", f"apktool{ext}")
    except Exception as e:
        err(0,f"URLlib: {e}") 
        _ = False
        
    if not _:
        err(0,"Неможливо завантажити важливі інструменти")
        exit(-1)

    return
 
def isAlreadyIn(li_st, id):
    for x in li_st:
        if x[0] == id:
            return True
    
    return False
    
def reformat_list(li_st, fmt, uniqued):
    global poutCount
    finalli = []
    if len(li_st) == 0:
        return finalli

    for x in li_st:
        cid   = 0
        chash = ""
        cname = ""
        ctype = -1
        coff  = -1
        
        for y in x:
            if len(str(y)) == 32 and re.match(r'[0-9a-f]{32}', str(y)):
                chash = y
                continue
            
            if isinstance(y, int):
                if cid > 0 and 1 <= y <= 10:
                    if ctype < 0:
                        ctype = y
                        
                    if coff < 0:
                        coff = y
                    
                    continue
                else:
                    cid = y
            
            yl = str(y).lower()
            yl = ''.join(char for char in yl if not char.isspace())
            yl = yl.replace("telegram", "")
            
            if (yl == "android") or (yl == "androidos") or (yl == "androidwear") or (yl == "blackberry") or (yl == "lineageos"):
                ctype = 1
                continue
            
            if (yl == "ios") or (yl == "iphone") or (yl == "iphoneos"):
                ctype = 2
                continue
            
            if (yl == "web") or (yl == "web..org"):
                ctype = 3
                continue
            
            if (yl == "tdesktop") or (yl == "desktop") or (yl == "windows") or (yl == "windowsos") or (yl == "mac") or (yl == "macos") or (yl == "macosx") or (yl == "linux") or (yl == "ubuntu") or (yl == "flatpak") or (yl == "xubuntu") or (yl == "unix") or (yl == "bsd") or (yl == "freebsd") or (yl == "cli")  or (yl == "tg-cli")  or (yl == "tgcli")  or (yl == "cli-tg")  or (yl == "telethon"):
                ctype = 0
                continue
                
            cname = y
        
        if ctype < 0:
            ctype = 0
            
        if coff < 0:
            coff = int(isAlreadyIn(OFFICIAL_LIST, cid))
                
        if uniqued:
            if isAlreadyIn(li_st, x[0]):
                continue
            
        if fmt:
            if poutCount > 0:
                wu(jss[4])
            wu(f'{jss[6]}{jss[0]}{cid}{jss[5]}"{chash}"{jss[5]}{ctype}{jss[5]}"{cname}"{jss[5]}{coff}{jss[1]}')
            poutCount = poutCount + 1
                
            finalli.append([cid, chash, ctype, cname, coff])
        else:
            if poutCount > 0:
                wu(jss[4])
            wu(f'{jss[6]}{jss[0]}{cid}{jss[5]}"{chash}"{jss[5]}"{cname}"{jss[1]}')
            poutCount = poutCount + 1
                
            finalli.append([cid, chash, cname])
            
    return finalli
     
def append_res(whatto, li_st, apptype, toformat, uniqued):
    global poutCount
    if uniqued:
        if isAlreadyIn(li_st, whatto[0]):
            return 1

    if toformat:
        coff = int(isAlreadyIn(OFFICIAL_LIST, whatto[0]))
        if toCons:
            if poutCount > 0:
                wu(jss[4])
            wu(f'{jss[6]}{jss[0]}{whatto[0]}{jss[5]}"{whatto[1]}"{jss[5]}{apptype}{jss[5]}"{whatto[2]} by {whatto[3]}"{jss[5]}{coff}{jss[1]}')
            poutCount = poutCount + 1
            
        li_st.append([whatto[0], whatto[1], apptype, whatto[2] + " by " + whatto[3], coff])
    else:
        if toCons:
            if poutCount > 0:
                wu(jss[4])
            wu(f'{jss[6]}{jss[0]}{whatto[0]}{jss[5]}"{whatto[1]}"{jss[5]}"{whatto[2]}"{jss[1]}')
            poutCount = poutCount + 1
            
        li_st.append([whatto[0], whatto[1], whatto[2]])
        
    return 1
    
def extract_api_from_smali(content):
    lines = content.split('\n')
    api_id = None
    api_hash = None
    current_v = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Match const for integer
        id_const_match = re.match(r'const(?:/16|/4)? v(\d+), (0x[\da-fA-F]+|\d+)', line)
        if id_const_match:
            value = id_const_match.group(2)
            current_v[id_const_match.group(1)] = int(value, 16) if value.startswith('0x') else int(value)
            continue
        
        # Match const-string for hash
        hash_const_match = re.match(r'const-string(?:/jumbo)? v(\d+), "([0-9a-f]{32})"', line)
        if hash_const_match:
            current_v[hash_const_match.group(1)] = hash_const_match.group(2)
            continue
        
        # Match sput for CLIENT_ID
        sput_id_match = re.match(r'sput(?:-wide)? v(\d+), .*?(APP|API)_ID:I', line, re.IGNORECASE)
        if sput_id_match:
            reg = sput_id_match.group(1)
            if reg in current_v:
                api_id = current_v[reg]
            continue
        
        # Match sput-object for CLIENT_HASH
        sput_hash_match = re.match(r'sput-object v(\d+), .*?(APP|API)_HASH:Ljava/lang/String;', line, re.IGNORECASE)
        if sput_hash_match:
            reg = sput_hash_match.group(1)
            if reg in current_v:
                api_hash = current_v[reg]
            continue
        
        # For direct = assignments in fields
        direct_id_match = re.search(r'(APP|API)_ID:I = (0x[\da-fA-F]+|\d+)', line, re.IGNORECASE)
        if direct_id_match:
            value = direct_id_match.group(2)
            api_id = int(value, 16) if value.startswith('0x') else int(value)
        
        direct_hash_match = re.search(r'(APP|API)_HASH:Ljava/lang/String; = "([0-9a-f]{32})"', line, re.IGNORECASE)
        if direct_hash_match:
            api_hash = direct_hash_match.group(2)
    
    return api_id, api_hash

def extract_app_name_and_developer(output_dir):
    manifest_path = os.path.join(output_dir, 'AndroidManifest.xml')
    strings_path = os.path.join(output_dir, 'res', 'values', 'strings.xml')
    
    app_name = "Secret"
    developer = "No one"
    
    if os.path.exists(manifest_path):
        manifest_tree = ET.parse(manifest_path)
        manifest_root = manifest_tree.getroot()
        
        package = manifest_root.get('package')
        if package:
            developer = package  # Якщо немає повної назви розробника, то використовуватиметься назва пакету, тобто щось накшталт org.telegram.android...
        
        application = manifest_root.find('application')
        if application:
            label = application.get('{http://schemas.android.com/apk/res/android}label')
            if label and label.startswith('@string/'):
                if os.path.exists(strings_path):
                    for string in ET.parse(strings_path).getroot().findall('string'):
                        name = string.get('name')
                        if name == label.split('/')[-1]:
                            app_name = string.text
                            break
    
    return app_name, developer

def extract_from_apk(apk_path, output_dir):
    if shutil.which("apktool") is None:
        if not toCons:
            print(f"{FGR}[УВАГА] Необхідно мати APKTool для цього: https://ibotpeaches.github.io/Apktool/{STA}")
        if cnfrm("Встановити автоматично?"):
            download_tools()
        else:
            exit(1)
            return
        
    
    if not toCons:
        print("Обробка: " + os.path.basename(apk_path))
    
    if os.path.isdir(output_dir):
        log("Вихідний каталог вже існує, пропуск розбірки")
    else:
        try:
            ok = True
            _ = subprocess.run(["apktool.bat", "d", apk_path, "-o", output_dir, "-f"],
            stdout=(sys.stdout if logm else subprocess.PIPE),
            stderr=(subprocess.PIPE if toCons else sys.stderr),
            stdin=subprocess.DEVNULL,
            text=True, check=True)
        except e:
            ok = False
        if (_.stderr is None or _.stderr == "") and ok:
            log(f"Застосунок розібрано до '{output_dir}'")
        

    # Пошук у розібраному коді
    api_id = None
    api_hash = None
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith(('.smali', '.xml', '.java', '.smol', '.small', '.smal')):
                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    api_id, api_hash = extract_api_from_smali(content)
                    if api_id and api_hash:
                        break
        if api_id and api_hash:
            break

    # У випадку невдачі, виконати прямий пошук у APK...
    if not api_id or not api_hash:
        with open(apk_path, 'rb') as f:
            data = f.read()
            # Пошук відомих CLIENT_ID у форматі little-endian
            for target_id in OFFICIAL_LIST:
                id_bytes = int.to_bytes(target_id[0], 4, 'little')
                offset = data.find(id_bytes)
                if offset != -1:
                    api_id = target_id[0]
                    if not toCons:
                        print(FGG + f"Знайдено: CLIENT_ID={api_id} на позиції 0x{offset:X}" + STA)

    app_name, developer = extract_app_name_and_developer(output_dir)
    
    if not toCons:
        if api_id and api_hash:
            print(FGG + f"Отримано: CLIENT_ID={api_id}, CLIENT_HASH={api_hash}" + STA)
        else:
            err(0,"Неможливо отримати CLIENT_ID або CLIENT_HASH !")
        
        print()
        
    return api_id, api_hash, app_name, developer

if __name__ == '__main__':
    init()
    subact = 0
    appsTotal = 0
    appsComplete = 0
    global poutCount, foutJSON
    poutCount = 0
    foutJSON = None
    ids = []
    ids2 = []
    
    expdir = ""
   
    uniqued = False
    fmt = False
    toCons = False
    
    # [ArrayStartCode, ArrayEndCode, StartCode, EndCode, ArrayElementSeparator, ArrayEndSeparator, ArrayStartSeparator, StartCodeAppendix, EndCodePrependix
    jss = ['{', '}',"{","}",", ",",", os.linesep + "\t", "", os.linesep]
    JSS_MFS = ["jss=", "jsonsyntax=", "jsonsyntaxis=", "jsonsyntacsys=", "jsonsyntaxys=", "жск=", "жсс=", "сінтжс=", "синтжс=", "жсонс=", "jsons=", "osf=", "фвс="]
    tc = ["-json", "-js", "-j",  "-d",  "-н", "-ж", "-к"]
    mjs = ["-min", "-minjs", "-minjson", "-minified", "-mini", "-мінімізований", "-мін", "-мінжс", "-мініжсон", "-міні"]
    asepF = ["-addsepf", "-addendum", "-appendix", "-forceseparator", "-additionalseparator", "-додроз", "-дрз"]
    addSepF = False
    expjs = ""
    
    
    if len(sys.argv) < 2:
        print("Використання:" +
        "\npython " + os.path.basename(__file__) + " <ФАЙЛ/каталог> [<каталог для розібраних>] [<вивід: .json масив>]"
        "\n-i -u -у Ігнорувати повторювані CLIENT_ID"
        "\n-f -ф Використовувати форматування ХрюкоГраму"
        "\n-s -д -з Не виводити докладний звіт"
        "\n" + " ".join(mjs) + " JSON без пробілів"
        "\n" + " ".join(tc) + " Виводити напряму фінальний JSON у консоль"
        "\n" + " ".join(asepF) + " Додавати роздільник у кінцевий елемент JSON"
        "\n-" + " -".join(JSS_MFS) + " Задати синтаксис JSON стрічкою або Python-скриптом"
        "\n-" + " -".join(validconfall) + " Автоматичне підтвердження/скасування дій, потребуючих втручання"
        )
        sys.exit(1)
    
    appf = sys.argv[1]
    
    # Обробка опцій
    if len(sys.argv) > 2:
        for x in range(2, len(sys.argv)):
            rsError = True
            arx = sys.argv[x].lower()
            arx = ''.join(char for char in arx if not char.isspace())
            if len(arx) < 1:
                continue
                
            if (arx == "clean") or (arx == "clean-up") or (arx == "clenup") or (arx == "clean_up"):
                subact = 1
                continue
                
            if (arx == "-і") or (arx == "-i") or (arx == "-у") or (arx == "-u"):
                uniqued = True
                continue
            
            if (arx == "-f") or (arx == "-ф"):
                fmt = True
                continue
                
            if (arx == "-д") or (arx == "-з") or (arx == "-s"):
                logm = False
                continue    
                
            if arx in tc:
                toCons = True
                logm = False
                continue    
                
            if arx in aSepF:
                addSepF = True
                continue
                
            if arx in mjs:
                jss = ['{','}',"{","}",",",",","","",""]
                continue
                
            if (expjs == "") and (arx.endswith(".json")):
                expjs = sys.argv[x]
                continue
            else:
                if (expdir == "") and (pathlib.Path(sys.argv[x]).is_dir()):
                    expdir = sys.argv[x]
                    continue
                
            if arx[1] == "-":
                arx = arx[1:]
                if arx in validconfall:
                    if validconfall[arx]:
                        yes_to_all = True
                    else:
                        no_to_all = True
                    continue
                    
                for ss in JSS_MFS:
                    if arx.startswith(ss):
                        arx = arx[len(ss):]
                        if os.path.is_file(arx) and ( arx.endswith(".py") or arx.endswith(".py'") or arx.endswith('.py"')):
                            with open(ss, "r") as f:
                                _ = f.read()
                                f.close()
                                exec(_)
                        else:
                            xCurr = 0
                            for y in ss.split(''):
                                jss[xCurr] = y
                                xCurr = xCurr + 1
              
                        rsError = False
                        break
                    
            if rsError:
                err(1,f"Невідома опція: {sys.argv[x]}")
                exit(1)
    
    if expdir == "":
        expdir = os.path.join((appf if pathlib.Path(appf).is_dir() else pathlib.Path(appf).parent), "extracts")
        
    if subact == 0:
        if os.path.exists(expjs):
            f = open(expjs)  
            try:
                ids2 = json.load(f)
            except ValueError as e:
                ids2 = [] 
                err(2,f"Збій читання файлу '{expjs}': {e}")
            f.close()
    
        if expjs != "":
            foutJSON = open(expjs, "w")
        
        wu(jss[2] + jss[7])
    
        if pathlib.Path(appf).is_dir():
            apps = os.listdir(appf)
        else:
            _, ext = os.path.splitext(appf)
            ext = ext.lower()[1:]
            if ext in SUPP_EXTS:
                apps = [appf]
                appf = pathlib.Path(appf).parent
            else:
                apps = []
                err(2,f"Непідтримуваний формат: {ext}")
            
           
        for app_path in apps:
            if os.path.isfile:
                _, ext = os.path.splitext(app_path)
                ext = ext.lower()[1:]
            else:
                ext = ">.<"
                
            if ext in SUPP_EXTS:
                appsTotal = appsTotal + 1
                appsComplete = appsComplete + append_res(globals()["extract_from_" + SUPP_EXTS[ext]](app_path, os.path.join(expdir, pathlib.Path(app_path).stem)), ids, 1, fmt, uniqued)

   
        if ids2 != []:
            reformat_list(ids2, fmt, uniqued)

        if (poutCount > 0) and addSepF:
            wu(jss[4])    
        wu(jss[8] + jss[3])
    
        if wposs(foutJSON):
            foutJSON.close()   
    
        if expjs != "":
            log(f"Дані збережено до: '{expjs}'")
            
    elif subact == 1:
        print("Очищення файлів...")
        for file in pathlib.Path(expdir).rglob("*"):
            appsTotal = appsTotal + 1
            try:
                file.unlink()
                logt(f"Спроба видалення: {file}")
                if file.exists():
                    err(0, "Немає повноважень")
            except Exception as e:
                err(1,f"  Збій видалення {file}: {e}")
            finally:
                appsComplete = appsComplete + 1
                log(f" Вдало видалено:  {file}")
                
    if not toCons:
            print( ( FGG if (appsTotal - appsComplete == 0) else FGR ) + f"[Готово]{STA} {appsComplete} з {appsTotal} оброблено!") 
    