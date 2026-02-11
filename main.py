# 🤖 FINANCE AGENT AI STRATEJİ MOTORU ENTEGRASYONU
st.markdown("---")
if st.button("🚀 Finance Agent Stratejisini Al"):
    with st.spinner("Agent verileri derinlemesine analiz ediyor..."):
        # 1. Ham Veriyi ve Volatiliteyi Çek (Geliştirilmiş Fonksiyon)
        df_raw, vol_val = fa.get_stock_data(secim, period=periyot)
        
        if df_raw is not None:
            # 2. Gelişmiş Analiz Motorunu Çalıştır
            # Bu fonksiyon artık sadece fiyat değil, RSI ve Trendi de analiz ediyor
            analysis_results = fa.advanced_analysis(df_raw, vol_val)
            
            # 3. Profesyonel Raporu Oluştur (Markdown formatında)
            report_text = rg.generate_report(secim, analysis_results)
            
            # 4. Ekranda Midas Stili Kart İçinde Göster
            st.markdown("### 🕵️ Agent Strateji Raporu")
            st.markdown(f'<div class="agent-card">{report_text}</div>', unsafe_allow_html=True)
            
            # 5. Opsiyonel: Raporu TXT/MD Olarak İndir
            st.download_button(
                label="📄 Raporu Dosya Olarak Kaydet",
                data=report_text,
                file_name=f"FinanceAgent_{secim}.md",
                mime="text/markdown"
            )
        else:
            st.error("Agent veri çekme aşamasında bir sorunla karşılaştı.")
