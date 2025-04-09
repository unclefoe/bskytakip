import tkinter as tk
import sys

def kaynak_yolu(dosya_adi):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, dosya_adi)
    return dosya_adi


from tkinter import messagebox
import tkinter.ttk as ttk
from atproto import Client
from datetime import datetime
import threading
import webbrowser
import os
from PIL import Image, ImageTk

BLUESKY_MAVISI = "#0095ff"
YESIL = "#4CAF50"
ACIK_GRI = "#f2f2f2"

client = Client()

not_following_back = {}
you_dont_follow_back = {}

# Kullanıcı DID'ini handle'dan çöz
def resolve_did(handle):
    result = client.com.atproto.identity.resolve_handle({'handle': handle})
    return result.did

# Takip durumunu kontrol et ve tersine çevir
def toggle_follow(did, button, takip_ediliyor):
    try:
        if takip_ediliyor.get():
            # Takipten çık
            follow_uri = None
            cursor = None
            while True:
                params = {
                    "repo": client.me.did,
                    "collection": "app.bsky.graph.follow",
                    "limit": 100
                }
                if cursor:
                    params["cursor"] = cursor
                result = client.com.atproto.repo.list_records(params)
                for record in result.records:
                    if record.value["subject"] == did:
                        follow_uri = record.uri
                        break
                if follow_uri or not result.cursor:
                    break
                cursor = result.cursor
            if follow_uri:
                client.delete_follow(follow_uri)
                button.config(text="Takip Et")
                takip_ediliyor.set(False)
        else:
            client.com.atproto.repo.create_record({
                'repo': client.me.did,
                'collection': 'app.bsky.graph.follow',
                'record': {
                    'subject': did,
                    'createdAt': datetime.utcnow().isoformat() + 'Z',
                }
            })
            button.config(text="Takipten Çık")
            takip_ediliyor.set(True)
    except Exception as e:
        messagebox.showerror("Hata", f"Hareket tamamlanamadı:\n{str(e)}")

# Uygulama üstünde çıkan özel hata penceresi
def hata_goster(mesaj):
    hata_pencere = tk.Toplevel(pencere)
    hata_pencere.title("Hata")
    hata_pencere.geometry("300x120")
    hata_pencere.configure(bg="white")

# Ayarlar menüsü
pencere = tk.Tk()
pencere.withdraw()  # Splash sırasında gizle
pencere.title("BSKY Takipçi Kontrol")
pencere.geometry("375x300")
pencere.configure(bg="white")

# Menü tanımı burada olacak
menubar = tk.Menu(pencere)
ayarlar_menu = tk.Menu(menubar, tearoff=0)
ayarlar_menu.add_command(label="Sürüm: v1.0", command=lambda: messagebox.showinfo("Sürüm Bilgisi", "Uygulama Sürümü: v1.0"))
ayarlar_menu.add_command(label="Geri Bildirim Gönder", command=lambda: webbrowser.open("https://orgutsuz.bsky.social"))
ayarlar_menu.add_separator()
ayarlar_menu.add_command(label="Ayarları Sıfırla", command=lambda: reset_ayarlar())
menubar.add_cascade(label="⋮", menu=ayarlar_menu)
pencere.config(menu=menubar)

def reset_ayarlar():
    try:
        os.remove("ayarlar.txt")
        messagebox.showinfo("Sıfırla", "Ayarlar başarıyla sıfırlandı.")
    except:
        messagebox.showwarning("Sıfırla", "Ayar dosyası bulunamadı.")

    hata_pencere.attributes("-topmost", True)  # Uygulamanın üzerinde açılır

    # Pencereyi ana pencereyle ortalayalım
    pencere.update_idletasks()
    x = pencere.winfo_x() + (pencere.winfo_width() // 2) - 150
    y = pencere.winfo_y() + (pencere.winfo_height() // 2) - 60
    hata_pencere.geometry(f"+{x}+{y}")

    tk.Label(hata_pencere, text=mesaj, bg="white", fg="red", font=("Arial", 10), wraplength=280).pack(pady=20)
    tk.Button(hata_pencere, text="Tamam", command=hata_pencere.destroy, bg=BLUESKY_MAVISI, fg="white").pack(pady=(0, 10))

# Listeyi göster
def goster_liste(tip):
    canvas.yview_moveto(0)
    liste_container.pack(fill="both", expand=True)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for widget in frame_liste.winfo_children():
        widget.destroy()

    if tip == "geri_takip_olmayanlar":
        data = not_following_back
    else:
        data = you_dont_follow_back

    if not data:
        tk.Label(frame_liste, text="Bu listede kimse yok 😎", fg="gray", bg="white").pack(pady=10)
        return


    for handle, did in sorted(data.items()):
        row = tk.Frame(frame_liste, bg="white")
        row.pack(fill="x", padx=10, pady=3,)

        tk.Label(row, text=handle, width=34, anchor="w", bg="white", fg="black", wraplength=200).pack(side="left", padx=(5, 0))

        takip_ediliyor = tk.BooleanVar(value=(tip == "geri_takip_olmayanlar"))
        btn = tk.Button(
            row,
            text="Takipten Çık" if takip_ediliyor.get() else "Takip Et",
            width=12,
            bg=BLUESKY_MAVISI,
            fg="white",
            relief="flat",
            padx=0,
            pady=0
        )
        btn.pack(side="right", anchor="e", padx=(0, 0))
        btn.config(command=lambda d=did, b=btn, v=takip_ediliyor: toggle_follow(d, b, v))

        # Ayıraç çizgi
        tk.Frame(frame_liste, bg="black", height=1).pack(fill="x", padx=5, pady=2)

    canvas.update_idletasks()
    pencere.geometry(f"375x{min(720, 300 + len(data) * 40)}")

# Kontrol işlemi
def kontrol_et():
    username_raw = entry_kullanici.get().strip()
    password = entry_sifre.get().strip()
    suffix = suffix_var.get().strip()

    if suffix:
        username = username_raw + suffix
    else:
        username = username_raw

    progress.pack(pady=5)
    progress["value"] = 0
    frame_tablar.pack_forget()
    liste_container.pack_forget()
    pencere.geometry("375x300")

    def yavas_yukleme(progress_bar, pencere, bitirme_durumu):
        if not bitirme_durumu["bitti"]:
            if progress_bar["value"] < 99:
                progress_bar["value"] += 1
                pencere.after(30, lambda: yavas_yukleme(progress_bar, pencere, bitirme_durumu))
        else:
            progress_bar["value"] = 100
            progress_bar.pack_forget()
            frame_tablar.pack(pady=10)
            pencere.geometry("375x300")

    bitirme_durumu = {"bitti": False}
    yavas_yukleme(progress, pencere, bitirme_durumu)

    def arkaplan():
        global not_following_back, you_dont_follow_back

        try:
            client.login(username, password)
        except Exception as e:
            progress.pack_forget()
            hata_mesaji = str(e).lower()

            if "unauthorized" in hata_mesaji or "invalid" in hata_mesaji:
                hata_goster("Kullanıcı adı veya şifre hatalı.")
                with open("error.log", "a", encoding="utf-8") as log:
                    log.write(f"{datetime.now()} - Giriş Hatası: {str(e)}\n")
            else:
                messagebox.showerror("Giriş Başarısız", f"Beklenmeyen bir hata oluştu:\n{str(e)}")
            return

        def get_all_handles(api_call):
            handles = {}
            cursor = None
            while True:
                result = api_call({'actor': client.me.did, 'limit': 100, 'cursor': cursor})
                users = result.follows if hasattr(result, 'follows') else result.followers
                for user in users:
                    handles[user.handle] = user.did
                if not result.cursor:
                    break
                cursor = result.cursor
            return handles

        following = get_all_handles(client.app.bsky.graph.get_follows)
        followers = get_all_handles(client.app.bsky.graph.get_followers)

        not_following_back = {h: d for h, d in following.items() if h not in followers}
        you_dont_follow_back = {h: d for h, d in followers.items() if h not in following}

        btn_takip_olmayanlar.config(text=f"Geri Takip Etmeyenler ({len(not_following_back)})")
        btn_takip_etmediklerin.config(text=f"Geri Takip Etmediklerin ({len(you_dont_follow_back)})")
        bitirme_durumu["bitti"] = True
        progress.pack_forget()
        frame_tablar.pack(pady=10)
        pencere.geometry("375x300")

    threading.Thread(target=arkaplan).start()

# Arayüz
pencere = tk.Tk()
def uygulamayi_kapat():
    pencere.destroy()
    sys.exit()

pencere.protocol("WM_DELETE_WINDOW", uygulamayi_kapat)
pencere.withdraw()  # Ana pencereyi gizle
pencere.iconbitmap(kaynak_yolu("logo.ico"))

# SPLASH SCREEN BAŞLANGIÇ
splash = tk.Toplevel()
splash.overrideredirect(True)
splash.configure(bg="white")

logo_img = Image.open(kaynak_yolu("logo.png"))
logo_img = logo_img.resize((80, 80))
logo_tk = ImageTk.PhotoImage(logo_img)

tk.Label(splash, image=logo_tk, bg="white").pack(pady=(30, 10))

# Splash boyutları
splash_w, splash_h = 300, 200

# Ekran boyutunu al
ekran_genislik = pencere.winfo_screenwidth()
ekran_yukseklik = pencere.winfo_screenheight()

x = (ekran_genislik // 2) - (splash_w // 2)
y = (ekran_yukseklik // 2) - (splash_h // 2)

splash.geometry(f"{splash_w}x{splash_h}+{x}+{y}")

tk.Label(splash, text="Bluesky Takipçi Kontrol", font=("Arial", 14, "bold"), fg=BLUESKY_MAVISI, bg="white").pack(expand=True)
tk.Label(splash, text="Yükleniyor...", font=("Arial", 10), fg="gray", bg="white").pack(pady=(0, 20))


def splash_kapat():
    # Ana pencereyi de ortala
    pencere.update_idletasks()
    w, h = 375, 300  # pencerenin sabit boyutu
    ekran_w = pencere.winfo_screenwidth()
    ekran_h = pencere.winfo_screenheight()
    x = (ekran_w // 2) - (w // 2)
    y = (ekran_h // 2) - (h // 2)
    pencere.geometry(f"{w}x{h}+{x}+{y}")

    splash.destroy()
    pencere.deiconify()

    # Menü (üstte görünür)
    menubar = tk.Menu(pencere)
    ayarlar_menu = tk.Menu(menubar, tearoff=0)
    ayarlar_menu.add_command(label="Sürüm: v1.0", command=lambda: messagebox.showinfo("Sürüm Bilgisi", "Uygulama Sürümü: v1.0"))
    ayarlar_menu.add_command(label="Geri Bildirim Gönder", command=lambda: webbrowser.open("https://orgutsuz.bsky.social"))
    ayarlar_menu.add_separator()
    ayarlar_menu.add_command(label="Ayarları Sıfırla", command=lambda: reset_ayarlar())
    menubar.add_cascade(label="Menü", menu=ayarlar_menu)
    pencere.config(menu=menubar)


pencere.after(2000, splash_kapat)  # 2 saniye sonra geçiş yap
# SPLASH SCREEN BİTİŞ

pencere.title("Bluesky Takipçi Kontrol")
pencere.geometry("375x300")
pencere.configure(bg="white")



def reset_ayarlar():
    try:
        os.remove("ayarlar.txt")
        messagebox.showinfo("Sıfırla", "Ayarlar başarıyla sıfırlandı.")
    except:
        messagebox.showwarning("Sıfırla", "Ayar dosyası bulunamadı.")


# Logo ve Uygulama ismi
logo_frame = tk.Frame(pencere, bg="white", bd=2)
logo_frame.pack(fill="x")
tk.Label(logo_frame, text="Bluesky Takipçi Kontrol", font=("Arial", 14), fg=BLUESKY_MAVISI, bg="white").pack(pady=10)

# Kullanıcı Adı
username_var = tk.StringVar()
suffix_var = tk.StringVar(value=".bsky.social")


tk.Label(pencere, text="Kullanıcı Adı:", bg="white").pack()
user_frame = tk.Frame(pencere, bg="white")
user_frame.pack()

entry_kullanici = tk.Entry(user_frame, textvariable=username_var, width=20,
                           highlightthickness=2, highlightbackground=BLUESKY_MAVISI,
                           bg=ACIK_GRI, fg="black")
entry_kullanici.pack(side="left")
suffix_entry = tk.Entry(user_frame, textvariable=suffix_var, width=13,
                        highlightthickness=2, highlightbackground=BLUESKY_MAVISI,
                        bg=ACIK_GRI, fg="black")
suffix_entry.pack(side="left", padx=(5, 0))
suffix_entry.insert(0, ".bsky.social")  # 👈 En önemli satır!

# Şifre
tk.Label(pencere, text="Şifre:", bg="white").pack()
password_frame = tk.Frame(pencere, bg="white")
password_frame.pack()
password_var = tk.StringVar()
entry_sifre = tk.Entry(password_frame, textvariable=password_var, show="*", width=25, highlightthickness=2, highlightbackground=BLUESKY_MAVISI, bg=ACIK_GRI)
entry_sifre.pack(side="left")

def toggle_password():
    if entry_sifre.cget("show") == "*":
        entry_sifre.config(show="")
        btn_goster.config(text="Gizle")
    else:
        entry_sifre.config(show="*")
        btn_goster.config(text="Göster")

btn_goster = tk.Button(password_frame, text="Göster", command=toggle_password, bg=BLUESKY_MAVISI, fg="white")
btn_goster.pack(side="left", padx=5)

# Enter tuşu
entry_kullanici.bind("<Return>", lambda e: kontrol_et())
entry_sifre.bind("<Return>", lambda e: kontrol_et())

# Kontrol butonu + progress bar
tk.Button(pencere, text="Kontrol Et", command=kontrol_et, bg=BLUESKY_MAVISI, fg="white", padx=20, pady=5).pack(pady=10)
progress = ttk.Progressbar(pencere, orient="horizontal", mode="determinate", length=375)
progress["maximum"] = 100
progress["value"] = 0
style = ttk.Style()
style.theme_use('default')
style.configure("TProgressbar", troughcolor='white', background=YESIL)

# Sekme butonları
frame_tablar = tk.Frame(pencere, bg="white")
btn_takip_olmayanlar = tk.Button(frame_tablar, text="Geri Takip Etmeyenler", command=lambda: goster_liste("geri_takip_olmayanlar"), bg=BLUESKY_MAVISI, fg="white", padx=10, pady=5)
btn_takip_olmayanlar.pack(side="left", padx=5)
btn_takip_etmediklerin = tk.Button(frame_tablar, text="Geri Takip Etmediklerin", command=lambda: goster_liste("seni_takip_ettikler"), bg=BLUESKY_MAVISI, fg="white", padx=10, pady=5)
btn_takip_etmediklerin.pack(side="left", padx=5)

# Liste alanı için kapsayıcı
liste_container = tk.Frame(pencere, bg="white")

# Liste alanı + scroll
canvas = canvas = tk.Canvas(liste_container, width=355, bg="white", highlightthickness=0)
scrollbar = tk.Scrollbar(liste_container, orient="vertical", command=canvas.yview, width=15)
canvas.configure(yscrollcommand=scrollbar.set)
frame_liste = tk.Frame(canvas, bg="white")
canvas.create_window((0, 0), window=frame_liste, anchor="nw")
frame_liste.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

import webbrowser

# Profil bağlantısına tıklandığında tarayıcıyı açacak fonksiyon
def open_link(event):
    webbrowser.open_new("https://orgutsuz.bsky.social")

# Footer kısmı (düzenlenmiş)
footer = tk.Frame(pencere, bg="white")
footer.pack(fill="x", side="bottom", pady=5)

# Sürüm bilgisi
tk.Label(footer, text="v1.0", fg="gray", bg="white").pack(side="left", padx=(10, 0))

# Sol kısım: "Designed by"
dash_label = tk.Label(footer, text="Designed by", fg="gray", bg="white")
dash_label.pack(side="left", padx=(10, 0))

# Sol kısım: "Örgütsüz"
label_link = tk.Label(footer, text="Enki (E.A)", fg=BLUESKY_MAVISI, cursor="hand2", bg="white")
label_link.pack(side="left", anchor="w", padx=(0, 0)) 

# Sağ kısım: "Powered by ChatGPT"
tk.Label(footer, text="Powered by ChatGPT", fg="gray", bg="white").pack(side="right", padx=(0, 10))  # Sağa yasladık

# Profil bağlantısı: "Designed by Örgütsüz" metnine link ekliyoruz
label_link.bind("<Button-1>", open_link)

# Mouse tekerleğiyle kaydırma (Windows/macOS)
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)
canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

pencere.mainloop()
