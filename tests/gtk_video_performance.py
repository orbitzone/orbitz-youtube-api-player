"""Manual offline WebKit CPU benchmark. Run within the app runtime with/without DRI.
Creates only temporary synthetic H.264 media; never loads user preferences or YouTube.
CPU % sums this test and its live descendants (100% = one CPU core).
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
from gi.repository import Gtk, GLib, WebKit2


def cpu_ticks(pid):
    total = 0
    try:
        stat = Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()
        total += int(stat[11]) + int(stat[12])
        children = set()
        for task in Path(f'/proc/{pid}/task').iterdir():
            children.update((task/'children').read_text().split())
        for child in children:
            total += cpu_ticks(int(child))
    except (OSError, ValueError):
        pass
    return total


with tempfile.TemporaryDirectory(prefix='youtube-video-benchmark-') as temporary:
    clip = Path(temporary, 'synthetic.mp4')
    subprocess.run(['gst-launch-1.0', '-q', 'videotestsrc', 'num-buffers=150',
                    'pattern=ball', '!', 'video/x-raw,width=1920,height=1080,framerate=30/1',
                    '!', 'x264enc', 'speed-preset=ultrafast', 'tune=zerolatency',
                    '!', 'video/x-h264,profile=constrained-baseline', '!', 'h264parse',
                    '!', 'mp4mux', '!', 'filesink', 'location='+str(clip)], check=True)
    page = Path(temporary, 'index.html')
    page.write_text('<html style="background:black"><body style="margin:0;overflow:hidden">'
                    '<video id="v" src="synthetic.mp4" autoplay muted loop '
                    'style="width:100vw;height:100vh;object-fit:fill"></video></body></html>')
    manager = WebKit2.UserContentManager()
    manager.register_script_message_handler('benchmark')
    view = WebKit2.WebView(user_content_manager=manager)
    view.get_settings().set_media_playback_requires_user_gesture(False)
    window = Gtk.Window(title='Teste temporário de desempenho de vídeo')
    window.set_default_size(640, 360)
    window.add(view)
    cases = [(640, 360), (1280, 720)]
    results = []
    baseline = {}

    def begin_measure():
        baseline.update(ticks=cpu_ticks(os.getpid()), time=time.monotonic())
        GLib.timeout_add_seconds(5, end_measure)
        return False

    def end_measure():
        elapsed = time.monotonic()-baseline['time']
        cpu = (cpu_ticks(os.getpid())-baseline['ticks'])/os.sysconf('SC_CLK_TCK')/elapsed*100
        baseline['cpu_percent'] = round(cpu, 1)
        view.run_javascript('(()=>{const v=document.getElementById("v");window.webkit.messageHandlers.benchmark.postMessage(JSON.stringify({time:v.currentTime,paused:v.paused,ready:v.readyState,width:innerWidth,height:innerHeight,quality:v.getVideoPlaybackQuality()}));})();', None, None, None)
        return False

    def receive(_manager, message):
        data = json.loads(message.get_js_value().to_string())
        data['cpu_percent'] = baseline['cpu_percent']
        if data['paused'] or data['ready'] < 2:
            raise RuntimeError('Synthetic video did not play: '+str(data))
        results.append(data)
        print(json.dumps(data), flush=True)
        if len(results) == len(cases):
            Gtk.main_quit()
        else:
            window.resize(*cases[len(results)])
            GLib.timeout_add_seconds(2, begin_measure)

    manager.connect('script-message-received::benchmark', receive)
    view.connect('load-changed', lambda _v, event: GLib.timeout_add_seconds(3, begin_measure)
                 if event == WebKit2.LoadEvent.FINISHED else None)
    view.load_uri(page.as_uri())
    window.show_all()
    GLib.timeout_add_seconds(25, lambda: Gtk.main_quit() or False)
    Gtk.main()
    window.destroy()
    if len(results) != len(cases):
        raise SystemExit('Incomplete benchmark')
