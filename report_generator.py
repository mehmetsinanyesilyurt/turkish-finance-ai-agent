class ReportGenerator:
    def create_markdown_report(self, data, analyst_comment):
        report = f"""
# 🚀 Finansal Analiz Raporu
**Tarih:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

## 📊 Piyasa Durumu
| Varlık | Fiyat | Günlük Değişim |
| :--- | :--- | :--- |
"""
        for asset, values in data.items():
            report += f"| {asset} | {values['price']} | {values['change']} |\n"
            
        report += f"\n## 🧠 Stratejik Analiz\n{analyst_comment}\n"
        report += "\n--- \n*Not: Bu rapor yapay zeka tarafından üretilmiştir. Yatırım tavsiyesi değildir.*"
        return report
