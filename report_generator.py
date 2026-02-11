# report generator for turkish finance ai agent
# generates markdown reports from analysis data

import os
from datetime import datetime


def generate_report(symbol, analysis):
    """Generate a markdown report from analysis results."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    trend = "📈 Yükseliş" if analysis["pct_change"] > 0 else "📉 Düşüş"
    
    report = f"""# 🚀 Finansal Analiz Raporu
**Sembol:** {symbol}  
**Tarih:** {now}

## 📊 Piyasa Durumu
| Gösterge | Değer |
| :--- | :--- |
| Başlangıç Fiyatı | {analysis['start_price']:.2f} TL |
| Son Fiyat | {analysis['end_price']:.2f} TL |
| Değişim | {analysis['change']:.2f} TL |
| Yüzde Değişim | %{analysis['pct_change']:.2f} |
| Trend | {trend} |

---
*Not: Bu rapor otomatik olarak üretilmiştir. Yatırım tavsiyesi değildir.*
"""
    return report


def save_report(report, filename="sample_report.md"):
    """Save the report to a markdown file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)


class ReportGenerator:
    """Class-based report generator for advanced use cases."""
    
    def create_markdown_report(self, data, analyst_comment):
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        report = f"""
# 🚀 Finansal Analiz Raporu
**Tarih:** {now}

## 📊 Piyasa Durumu
| Varlık | Fiyat | Günlük Değişim |
| :--- | :--- | :--- |
"""
        for asset, values in data.items():
            report += f"| {asset} | {values['price']} | {values['change']} |\n"
            
        report += f"\n## 🧠 Stratejik Analiz\n{analyst_comment}\n"
        report += "\n--- \n*Not: Bu rapor yapay zeka tarafından üretilmiştir. Yatırım tavsiyesi değildir.*"
        return report
