Before working make sure to install all the modules listed in **requirements.txt**. If an error occures during the automatic IDE configuration, it may make sense to install latest versions of modules aviable on your Python interpretator (3.10 was used in that project).

**Python 3.11 is not supported by some of the modules yet.**

* **main.py** - main file to run the 3D visualization app. LMB to move the camera, RMB to zoom camera in and out, MMB to rotate the camera view. Press F1 to start logging the visualization, this process can't be paused though. Press F2 to stop logger and save the log file as *date_time*.json in parsed format. Press F3 to show or hide coordinates labels to debug drones positions.

* **player.py** - file to run the 3D log player app that can visualize drones movements stored within the chosen log. Can be paused and restarted with F1 and F2. Similiarly to main.py, F3 turns debugger on/off.

* **lps.py** - Locus LPS python module to get drones positions using RS-485 standart.

* **colorable_sphere.egg** - colorable sphere model in Panda3D native format to be used in the script.

* **logs** - folder for .json logs.
##

Перед началом работы необходимо установить требуемые модули согласно **requirements.txt**. В случае возникновения ошибки автоматической настройки среды разработки имеет смысл установить самые актуальные версии модулей под вашу версию интерпретатора Python (т.е. если она не соответствует 3.10).

**Python 3.11 ещё не поддерживается некоторыми из модулей на данный момент.**

* **main.py** - основной файл для запуска приложения 3D визуализации. Левая кнопка мыши передвигает камеру, правая кнопка мыши приближает и отдаляет изображение, колесико мыши вращает камеру. Нажмите F1 чтобы запустить логирование визуализации, но учитывайте, что этот процесс не может быть поставлен на паузу. Нажмите F2 чтобы остановить логер и сохранить файл с названием *дата_время*.json в запаршенном формате. Нажмите F3 чтобы отобразить или спрятать координаты дронов для дебага.

* **player.py** - файл для запуска плеера логов, который может визуализировать передвижения дронов записанные в выбранном логе. Можно поставить на паузу и перезапустить с помощью клавиш F1 и F2. Аналогично main.py, F3 включает или выключает дебаггер.

* **lps.py** - Python-модуль системы позиционирования Локус для получения координат дронов с помощью RS-485 стандарта.

* **colorable_sphere.egg** - окрашиваемая модель сферы в нативном формате Panda3D для использования в скрипте.

* **logs** - папка для хранения .json логов.
