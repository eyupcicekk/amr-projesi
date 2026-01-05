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
# --- 4. GÖRSELLEŞTİRME ---
st.markdown("---")
st.subheader("📊 Görsel Simülasyon (Teorik Limitler)")

def draw_scenario(ax, title, angle_deg, w_left, w_right, h, mode='rollover'):
    ax.set_title(f"{title}\nLimit: {angle_deg:.1f}°", fontsize=9, weight='bold')
    ax.set_aspect('equal')
    
    theta = np.radians(angle_deg)
    
    # Döndürme Fonksiyonu
    def rotate(x, y, t):
        x_new = x * np.cos(t) - y * np.sin(t)
        y_new = x * np.sin(t) + y * np.cos(t)
        return x_new, y_new

    # Zemin Çizimi
    ground_len = max(w_left, w_right) + h + 1
    gx = [-ground_len, ground_len]
    gy = [0, 0]
    rgx, rgy = [], []
    for i in range(2):
        rx, ry = rotate(gx[i], gy[i], theta)
        rgx.append(rx)
        rgy.append(ry)
    
    ax.plot(rgx, rgy, 'k-', lw=3)
    
    # Araç Kutusu
    box_x = [-w_left, w_right, w_right, -w_left, -w_left]
    box_y = [0, 0, h*1.5, h*1.5, 0]
    
    rbox_x, rbox_y = [], []
    for i in range(len(box_x)):
        rx, ry = rotate(box_x[i], box_y[i], theta)
        rbox_x.append(rx)
        rbox_y.append(ry)
        
    ax.fill(rbox_x, rbox_y, color='skyblue', alpha=0.6)
    ax.plot(rbox_x, rbox_y, 'b-', lw=2)
    
    # COG (0, h) konumunda
    rcog_x, rcog_y = rotate(0, h, theta)
    ax.plot(rcog_x, rcog_y, 'ro', zorder=5)
    
    # Yerçekimi Vektörü
    vec_len = h * 0.7
    ax.arrow(rcog_x, rcog_y, 0, -vec_len, head_width=0.1, head_length=0.1, fc='r', ec='r', lw=2)
    
    # Devrilme Referans Çizgisi
    if mode == 'rollover':
        ax.plot([0, 0], [0, h*2], 'k--', alpha=0.3, lw=1)
    
    limit_view = h + max(w_left, w_right) + 0.5
    ax.set_xlim(-limit_view, limit_view)
    ax.set_ylim(-1, limit_view + 1)
    ax.axis('off')

# Grafikleri Çiz
g1, g2, g3, g4 = st.columns(4)

with g1:
    fig1, ax1 = plt.subplots(figsize=(3,3))
    draw_scenario(ax1, "1. Kayma", limits['slide'], b/2, b/2, h, mode='slide')
    st.pyplot(fig1)

with g2:
    fig2, ax2 = plt.subplots(figsize=(3,3))
    # Yanalda araç genişliği b. Pivot merkezden b/2 uzaklıkta.
    draw_scenario(ax2, "2. Yanal", limits['lateral'], b/2, b/2, h)
    st.pyplot(fig2)

with g3:
    fig3, ax3 = plt.subplots(figsize=(3,3))
    # Yokuş yukarıda pivot arka teker (L_rear).
    draw_scenario(ax3, "3. Yokuş Yukarı", limits['uphill'], L_rear, L_front, h)
    st.pyplot(fig3)

with g4:
    fig4, ax4 = plt.subplots(figsize=(3,3))
    # Yokuş aşağıda pivot ön teker (L_front).
    draw_scenario(ax4, "4. Yokuş Aşağı", limits['downhill'], L_front, L_rear, h)
    st.pyplot(fig4)