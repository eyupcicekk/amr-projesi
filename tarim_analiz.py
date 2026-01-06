import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Sayfa Ayarları
st.set_page_config(page_title="Araç Stabilite Analizi", layout="wide")

st.title("🚜 Araç Denge ve Devrilme Analizi")
st.markdown("Bu uygulama, araç ölçülerine göre **teorik** devrilme/kayma limitlerini hesaplar ve güvenlik katsayısı ile gerçekçi sınırlar önerir.")

# --- 1. SOL MENÜ (GİRDİLER) ---
with st.sidebar:
    st.header("⚙️ Araç Parametreleri")
    
    st.subheader("Ölçüler")
    b = st.number_input("İz Genişliği (b) [m]", value=1.60, step=0.05, format="%.2f")
    h = st.number_input("Ağırlık Merkezi Yüksekliği (h) [m]", value=0.60, step=0.05, format="%.2f")
    
    st.subheader("Ağırlık Merkezi Konumu")
    L_rear = st.number_input("Arka Aks - COG Mesafesi [m]", value=0.40, step=0.05, format="%.2f")
    L_front = st.number_input("Ön Aks - COG Mesafesi [m]", value=1.20, step=0.05, format="%.2f")
    
    st.subheader("Çevresel Faktörler")
    mu = st.slider("Zemin Sürtünme Katsayısı (µ)", 0.1, 1.0, 0.60, step=0.05)
    
    st.markdown("---")
    st.subheader("🛡️ Güvenlik")
    # BURADA format="%.2f" ekleyerek kutu içindeki görünümü düzelttik
    safety_factor = st.number_input(
        "Güvenlik Katsayısı (SF)", 
        min_value=1.0, 
        value=1.50, 
        step=0.05,
        format="%.2f",
        help="Teorik fiziksel limiti bu sayıya bölerek 'Güvenli Çalışma Açısı' bulunur."
    )

# --- 2. HESAPLAMA FONKSİYONLARI ---
def calculate_limits(b, h, L_rear, L_front, mu):
    # 1. Kayma (Sliding)
    angle_slide_deg = np.degrees(np.arctan(mu))
    
    # 2. Yanal Devrilme (Lateral)
    angle_lateral_deg = np.degrees(np.arctan((b / 2) / h))
    
    # 3. Yokuş Yukarı (Uphill)
    angle_uphill_deg = np.degrees(np.arctan(L_rear / h))
    
    # 4. Yokuş Aşağı (Downhill)
    angle_downhill_deg = np.degrees(np.arctan(L_front / h))
    
    return {
        "slide": angle_slide_deg,
        "lateral": angle_lateral_deg,
        "uphill": angle_uphill_deg,
        "downhill": angle_downhill_deg
    }

# Hesaplamayı yap
limits = calculate_limits(b, h, L_rear, L_front, mu)

# En düşük limiti (Kritik Faktör) bul
min_angle_val = min(limits.values())
limiting_factor_key = [k for k, v in limits.items() if v == min_angle_val][0]

names = {
    "slide": "Zemin Kayması (Sliding)",
    "lateral": "Yanal Devrilme (Lateral)",
    "uphill": "Yokuş Yukarı (Longitudinal Uphill)",
    "downhill": "Yokuş Aşağı (Longitudinal Downhill)"
}

# --- 3. SONUÇ VE RAPORLAMA ---
col_res1, col_res2 = st.columns([2, 1])

with col_res1:
    st.header("📋 Sonuç ve Değerlendirme")
    
    st.error(f"⚠️ **Sınırlayıcı Faktör (KRİTİK):** {names[limiting_factor_key]} → **{min_angle_val:.1f}°**")
    
    st.markdown(f"""
    Araç **{min_angle_val:.1f}°** eğime ulaştığında fiziksel olarak dengesini kaybeder.
    Ancak süspansiyon ve lastik esnemeleri nedeniyle **gerçek limit daha düşüktür.**
    """)
    
    # --- FORMÜL VE DETAY KISMI ---
    with st.expander("📐 Hesaplama Detayları ve Formüller (Tıkla Gör)"):
        st.markdown("Hesaplamalarda kullanılan trigonometrik bağıntılar aşağıdadır:")
        
        # Her bir limit için döngü
        for key, val in limits.items():
            st.markdown("---") # Ayırıcı çizgi
            
            # Başlık ve Sonuç
            icon = "🔴" if key == limiting_factor_key else "✅"
            st.markdown(f"### {icon} {names[key]}: **{val:.1f}°**")
            
            # Formülleri Duruma Göre Seç
            if key == "slide":
                st.latex(r"\theta_{slide} = \arctan(\mu)")
                st.caption(f"Hesap: arctan({mu}) = {val:.1f}°")
                
            elif key == "lateral":
                st.latex(r"\theta_{lateral} = \arctan\left(\frac{b/2}{h}\right)")
                st.caption(f"Hesap: arctan(({b:.2f}/2) / {h:.2f}) = {val:.1f}°")
                
            elif key == "uphill":
                st.latex(r"\theta_{uphill} = \arctan\left(\frac{L_{rear}}{h}\right)")
                st.caption(f"Hesap: arctan({L_rear:.2f} / {h:.2f}) = {val:.1f}°")
                
            elif key == "downhill":
                st.latex(r"\theta_{downhill} = \arctan\left(\frac{L_{front}}{h}\right)")
                st.caption(f"Hesap: arctan({L_front:.2f} / {h:.2f}) = {val:.1f}°")

with col_res2:
    st.info(f"🛡️ **Güvenli Operasyon (SF: {safety_factor:.2f})**")
    
    safe_limit = min_angle_val / safety_factor
    st.metric(label="Maksimum Güvenli Eğim", value=f"{safe_limit:.1f}°", delta=f"Teorik: {min_angle_val:.1f}°")
    
    st.markdown(f"*Teorik limit ({min_angle_val:.1f}°), güvenlik katsayısına ({safety_factor:.2f}) bölünmüştür.*")

# --- 4. GÖRSELLEŞTİRME (HİBRİT: HEM BLOK HEM DAİRESEL TEKERLEK) ---
st.markdown("---")
st.subheader("🚜 Görsel Simülasyon (Gerçekçi Bakış Açısı)")
st.caption("Not: Yanal senaryolarda arkadan (blok teker), yokuş senaryolarında yandan (yuvarlak teker) görünüm kullanılır.")

def draw_scenario(ax, title, angle_deg, d1, d2, h, mode='rollover'):
    # d1: Sol/Arka mesafe, d2: Sağ/Ön mesafe
    ax.set_title(f"{title}\nLimit: {angle_deg:.1f}°", fontsize=10, weight='bold')
    ax.set_aspect('equal')
    theta = np.radians(angle_deg)
    
    # Döndürme Fonksiyonu (Tüm noktaları eğime göre çevirir)
    def rotate(x, y, t):
        return x * np.cos(t) - y * np.sin(t), x * np.sin(t) + y * np.cos(t)

    # --- ZEMİN ÇİZİMİ ---
    ground_len = max(abs(d1), abs(d2)) + h + 2
    gx, gy = [-ground_len, ground_len], [0, 0]
    rgx, rgy = [], []
    for i in range(2):
        rx, ry = rotate(gx[i], gy[i], theta)
        rgx.append(rx)
        rgy.append(ry)
    ax.plot(rgx, rgy, color='#5d4037', lw=4, solid_capstyle='round') # Toprak zemin

    # --- SENARYO TİPİNE GÖRE ÇİZİM ---
    
    # >>> MOD 1: YANDAN GÖRÜNÜŞ (Yokuş Yukarı/Aşağı) -> YUVARLAK TEKERLEKLER <<<
    if mode in ['uphill', 'downhill']:
        r_base = h * 0.25 # Baz tekerlek yarıçapı
        
        if mode == 'uphill':
            # Yokuş Yukarı: Sol=Arka(Büyük), Sağ=Ön(Küçük)
            x_rear, x_front = -d1, d2
            r_rear, r_front = r_base * 1.4, r_base * 0.9
            front_is_right = True
        else:
            # Yokuş Aşağı: Sol=Ön(Küçük), Sağ=Arka(Büyük)
            x_front, x_rear = -d1, d2 # d1 burada L_front, d2 L_rear olarak gelecek
            r_front, r_rear = r_base * 0.9, r_base * 1.4
            front_is_right = False

        # Daire Oluşturma Fonksiyonu
        def make_circle_points(cx, cy, r):
            angles = np.linspace(0, 2*np.pi, 30) # 30 noktalı daire
            xs = cx + r * np.cos(angles)
            ys = cy + r * np.sin(angles)
            return xs, ys

        # Tekerlek Koordinatlarını Hesapla ve Döndür
        # 1. Tekerlek (Sol)
        if mode == 'uphill': cx1, r1 = x_rear, r_rear
        else: cx1, r1 = x_front, r_front # downhill ise soldaki ön tekerdir
        
        c1x, c1y = make_circle_points(cx1, r1, r1) # Merkez Y yüksekliği r1 kadar yukarıda
        rc1x, rc1y = rotate(c1x, c1y, theta)
        
        # 2. Tekerlek (Sağ)
        if mode == 'uphill': cx2, r2 = x_front, r_front
        else: cx2, r2 = x_rear, r_rear
        
        c2x, c2y = make_circle_points(cx2, r2, r2)
        rc2x, rc2y = rotate(c2x, c2y, theta)

        # Tekerlekleri Çiz (İçleri dolu gri, kenarları siyah)
        ax.fill(rc1x, rc1y, color='#333333', zorder=4) # Sol Teker
        ax.plot(rc1x, rc1y, color='black', lw=2, zorder=4)
        ax.fill(rc2x, rc2y, color='#333333', zorder=4) # Sağ Teker
        ax.plot(rc2x, rc2y, color='black', lw=2, zorder=4)
        
        # Jantlar (Merkez noktalar)
        j1x, j1y = rotate(cx1, r1, theta)
        j2x, j2y = rotate(cx2, r2, theta)
        ax.plot(j1x, j1y, 'o', color='silver', markersize=5, zorder=5)
        ax.plot(j2x, j2y, 'o', color='silver', markersize=5, zorder=5)

        # Gövde (Yandan Görünüş)
        # Tekerleklerin üstünü birleştiren bir kutu
        base_h = min(r1, r2)
        body_h = h * 1.2
        box_x = [cx1, cx2, cx2, cx1, cx1]
        box_y = [base_h, base_h, base_h+body_h, base_h+body_h, base_h]
        
        rbox_x, rbox_y = [], []
        for i in range(len(box_x)):
            rx, ry = rotate(box_x[i], box_y[i], theta)
            rbox_x.append(rx)
            rbox_y.append(ry)
        
        ax.fill(rbox_x, rbox_y, color='forestgreen', alpha=0.9, zorder=3)
        ax.plot(rbox_x, rbox_y, color='#1b5e20', lw=2, zorder=3)

        # Baca/Egzoz (Sadece Yandan Görünüşte)
        chimney_x = cx2 if front_is_right else cx1
        chimney_x = chimney_x * 0.8
        c_x = [chimney_x, chimney_x]
        c_y = [base_h+body_h, base_h+body_h+(h*0.4)]
        rc_x, rc_y = rotate(np.array(c_x), np.array(c_y), theta)
        ax.plot(rc_x, rc_y, color='#424242', lw=4, solid_capstyle='round', zorder=2)


    # >>> MOD 2: ARKADAN GÖRÜNÜŞ (Yanal/Kayma) -> DİKDÖRTGEN TEKERLEKLER <<<
    else:
        # Eski kodundaki gibi blok tekerlekler
        wheel_radius = h * 0.25
        wheel_thickness = 8 
        
        # Sol Tekerlek (Blok)
        w1_x = [-d1, -d1]
        w1_y = [0, wheel_radius*2]
        # Sağ Tekerlek (Blok)
        w2_x = [d2, d2]
        w2_y = [0, wheel_radius*2]

        rw1_x, rw1_y = rotate(np.array(w1_x), np.array(w1_y), theta)
        rw2_x, rw2_y = rotate(np.array(w2_x), np.array(w2_y), theta)
        
        # Tekerlekleri Çiz (Kalın Çizgi Olarak)
        ax.plot(rw1_x, rw1_y, color='#212121', lw=wheel_thickness, solid_capstyle='round', zorder=2)
        ax.plot(rw2_x, rw2_y, color='#212121', lw=wheel_thickness, solid_capstyle='round', zorder=2)

        # Gövde (Arkadan Görünüş)
        body_bottom = wheel_radius * 0.8
        body_top = h * 1.6
        box_x = [-d1, d2, d2, -d1, -d1]
        box_y = [body_bottom, body_bottom, body_top, body_top, body_bottom]
        
        rbox_x, rbox_y = [], []
        for i in range(len(box_x)):
            rx, ry = rotate(box_x[i], box_y[i], theta)
            rbox_x.append(rx)
            rbox_y.append(ry)
            
        ax.fill(rbox_x, rbox_y, color='forestgreen', alpha=0.85, zorder=3)
        ax.plot(rbox_x, rbox_y, color='#1b5e20', lw=2, zorder=3)


    # --- ORTAK ELEMANLAR (COG ve Vektör) ---
    # COG her zaman yerden h kadar yukarıdadır (gövdeye bağlı döner)
    # Ancak görsel olarak tekerlek yarıçapını da hesaba katmalıyız ki havada durmasın
    cog_offset = 0 if mode not in ['uphill', 'downhill'] else (h*0.25)
    
    rcog_x, rcog_y = rotate(0, h + cog_offset, theta)
    ax.plot(rcog_x, rcog_y, marker='o', markersize=10, markerfacecolor='yellow', markeredgecolor='black', zorder=10)
    
    vec_len = h * 0.7
    ax.arrow(rcog_x, rcog_y, 0, -vec_len, head_width=0.15, head_length=0.15, fc='red', ec='red', lw=3, zorder=9)

    # Limit Ayarları
    limit_view = h + max(abs(d1), abs(d2)) + 1.5
    ax.set_xlim(-limit_view, limit_view)
    ax.set_ylim(-1, limit_view + 2)
    ax.axis('off')

# Grafikleri Çiz (Sütunlar)
g1, g2, g3, g4 = st.columns(4)

with g1:
    fig1, ax1 = plt.subplots(figsize=(3,3))
    # 1. Kayma -> Arkadan Görünüş (Blok Teker)
    draw_scenario(ax1, "1. Kayma", limits['slide'], b/2, b/2, h, mode='slide')
    st.pyplot(fig1)

with g2:
    fig2, ax2 = plt.subplots(figsize=(3,3))
    # 2. Yanal -> Arkadan Görünüş (Blok Teker)
    draw_scenario(ax2, "2. Yanal Devrilme", limits['lateral'], b/2, b/2, h, mode='lateral')
    st.pyplot(fig2)

with g3:
    fig3, ax3 = plt.subplots(figsize=(3,3))
    # 3. Yokuş Yukarı -> Yandan Görünüş (YUVARLAK Teker)
    draw_scenario(ax3, "3. Yokuş Yukarı", limits['uphill'], L_rear, L_front, h, mode='uphill')
    st.pyplot(fig3)

with g4:
    fig4, ax4 = plt.subplots(figsize=(3,3))
    # 4. Yokuş Aşağı -> Yandan Görünüş (YUVARLAK Teker)
    # L_front'u d1'e (sola), L_rear'ı d2'ye (sağa) veriyoruz ki ön teker aşağıda kalsın
    draw_scenario(ax4, "4. Yokuş Aşağı", limits['downhill'], L_front, L_rear, h, mode='downhill')
    st.pyplot(fig4)