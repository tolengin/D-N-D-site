# -*- coding: utf-8 -*-
"""
Sesleri site için hazırlar.
Girdi:  gorseller/ses-ham/*.mp3   (Freesound'dan indirilenler ve Suno şarkısı; ham hâlleri, GitHub'a gitmez)
Çıktı:  ses/<ad>.mp3               sitenin çaldığı küçük dosyalar
Çalıştırma (proje klasöründe):  python araclar\\ses_hazirla.py
Gerekenler: Python ve imageio-ffmpeg (pip install imageio-ffmpeg; içinde ffmpeg getirir).

Ne yapar?
1) Efektler (zar, kağıt, kupa…): başındaki sessizliği kırpar (tıklayınca ses gecikmesin), en yüksek yeri -1 dB'e
   getirir (hepsi aynı güçte olsun; aralarındaki denge sitede SES.vol ile ayarlanır), tek kanal 64 kbps.
2) Döngüler (ambiyans, şömine, gece): istenen uzunlukta keser, sesini eşitler ve sonunu başına 2 sn'lik geçişle
   bağlar; böylece döndükçe "dikiş" duyulmaz. Tek kanal 64 kbps.
3) Müzik: sesini eşitler, çift kanal 96 kbps.
Yeni ses eklemek: ham dosyayı gorseller/ses-ham/'a koy, aşağıdaki listeye ekle, betiği çalıştır.
"""
import pathlib, re, subprocess, sys
import imageio_ffmpeg

KOK = pathlib.Path(__file__).resolve().parent.parent
HAM, CIKTI = KOK / 'gorseller' / 'ses-ham', KOK / 'ses'
FF = imageio_ffmpeg.get_ffmpeg_exe()

EFEKTLER = ['zar-salla', 'zar-yuvarlan-1', 'zar-yuvarlan-2', 'zar-yuvarlan-3', 'kagit-ac', 'kagit-ac-rulo', 'kagit-kapa',
            'kapi-ac', 'gecis', 'adim', 'kupa', 'tik', 'dogal-20', 'dogal-1', 'ilham', 'katildi']
DONGULER = {'ambiyans': 36, 'ambiyans-2': 27, 'ates': 40, 'gece': 40}   # ad: uzunluk (sn, ham dosyanın başından)
MUZIK = {'Mead and Moonlight': 'muzik'}                                 # ham ad: sitedeki ad
DUZELT = {'zar-yuvarlan-3': -9.0}                                    # kulakla düzeltme (dB): diğer zarlardan çok yüksekti
GECIS = 2.0                                                             # döngünün dikiş geçişi (sn)


def ff(*args):
    r = subprocess.run([FF, '-hide_banner', '-y', *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    return r.stderr


def olc(dosya, on_filtre=''):                                           # (en yüksek yer, ortalama) dB
    out = ff('-i', str(dosya), '-af', (on_filtre + ',' if on_filtre else '') + 'volumedetect', '-f', 'null', '-')
    return float(re.search(r'max_volume: (-?[\d.]+) dB', out)[1]), float(re.search(r'mean_volume: (-?[\d.]+) dB', out)[1])


def efekt(ad):
    kirp = 'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.01'
    tepe, ort = olc(HAM / f'{ad}.mp3', kirp)
    kazan = min(-1.0 - tepe, -22.0 - ort) + DUZELT.get(ad, 0)           # ortalama -22 dB'e çek ama tepe -1 dB'i aşmasın
    ff('-i', str(HAM / f'{ad}.mp3'), '-af', f'{kirp},volume={kazan:.2f}dB', '-ac', '1', '-b:a', '64k', str(CIKTI / f'{ad}.mp3'))


def dongu(ad, uzun):
    g, son = GECIS, uzun
    # [g, son-g] gövde + (son-g..son kuyruğu kısılarak, 0..g başı açılarak) karışım → çalınan döngü son-g sn,
    # karışımın sonu gövdenin başına (g) birebir denk gelir
    filtre = (f'[0:a]atrim=0:{son},asetpts=N/SR/TB,aformat=channel_layouts=mono,loudnorm=I=-20:TP=-2,asplit=3[a][b][c];'
              f'[a]atrim={g}:{son - g},asetpts=N/SR/TB[govde];'
              f'[b]atrim={son - g}:{son},asetpts=N/SR/TB,afade=t=out:d={g}:curve=qsin[kuyruk];'
              f'[c]atrim=0:{g},asetpts=N/SR/TB,afade=t=in:d={g}:curve=qsin[bas];'
              f'[kuyruk][bas]amix=inputs=2:normalize=0[dikis];'
              f'[govde][dikis]concat=n=2:v=0:a=1[o]')
    ff('-i', str(HAM / f'{ad}.mp3'), '-filter_complex', filtre, '-map', '[o]', '-ar', '44100', '-b:a', '64k', str(CIKTI / f'{ad}.mp3'))


def muzik(ham, ad):
    ff('-i', str(HAM / f'{ham}.mp3'), '-af', 'loudnorm=I=-18:TP=-1.5', '-ar', '44100', '-ac', '2', '-b:a', '96k', str(CIKTI / f'{ad}.mp3'))


if __name__ == '__main__':
    CIKTI.mkdir(exist_ok=True)
    for ad in EFEKTLER:
        efekt(ad)
    for ad, uzun in DONGULER.items():
        dongu(ad, uzun)
    for ham, ad in MUZIK.items():
        muzik(ham, ad)
    for f in sorted(CIKTI.glob('*.mp3')):
        print(f'{f.name:22} {f.stat().st_size // 1024:5} KB')
