# 📁 GitHub Repository File Copier

أداة سطر أوامر بسيطة وقوية لنسخ الملفات من مستودع GitHub إلى آخر باستخدام الروابط المباشرة (Raw URLs). مثالية لمطوري الكيرنل الذين يحتاجون لدمج ملفات من عدة مستودعات أثناء عملية البناء.

## ✨ الميزات

- 🚀 **نسخ ملف واحد أو متعدد** بسهولة
- 📋 **دعم ملفات التكوين JSON** لنسخ ملفات متعددة دفعة واحدة
- 🔄 **فرض الاستبدال** للملفات الموجودة (--force)
- 🧪 **وضع التجربة** (Dry-run) لمعاينة ما سيتم نسخه
- 🛡️ **معالجة الأخطاء** مع رسائل واضحة
- 📦 **بدون مكتبات خارجية** - يستخدم Python القياسي فقط
- 🔗 **يدعم روابط GitHub العادية والـ Raw**

## 📋 المتطلبات

- Python 3.6 أو أحدث
- اتصال بالإنترنت

## 🔧 التثبيت

```bash
# تحميل السكربت
wget https://raw.githubusercontent.com/your-repo/copy_repo_files.py

# أو إنشاء الملف يدوياً
nano copy_repo_files.py

# منح صلاحية التنفيذ
chmod +x copy_repo_files.py




🚀 طرق الاستخدام

1. نسخ ملف واحد

```bash
python3 copy_repo_files.py -s المستخدم/المستودع -b الفرع -f المسار/الملف.c -d المسار/الهدف/الملف.c
```

مثال:

```bash
python3 copy_repo_files.py -s Samo1408/Builder_kernel -b m32-new -f fs/exec.c -d kernel_root/fs/exec.c
```

2. نسخ ملفات متعددة باستخدام JSON

قم بإنشاء ملف تكوين (مثال: copy_config.json):

```json
{
    "source_repo": "Samo1408/Builder_kernel",
    "branch": "m32-new",
    "files": [
        {
            "source": "fs/exec.c",
            "dest": "kernel_root/fs/exec.c"
        },
        {
            "source": "fs/open.c",
            "dest": "kernel_root/fs/open.c"
        },
        {
            "source": "kernel/reboot.c",
            "dest": "kernel_root/kernel/reboot.c"
        },
        {
            "source": "build.sh",
            "dest": "build.sh"
        }
    ]
}
```

ثم قم بتشغيل:

```bash
python3 copy_repo_files.py -c copy_config.json
```

3. فرض استبدال الملفات الموجودة

```bash
# لملف واحد
python3 copy_repo_files.py -s Samo1408/Builder_kernel -b m32-new -f fs/exec.c -d kernel_root/fs/exec.c --force

# لملفات متعددة من JSON
python3 copy_repo_files.py -c copy_config.json --force
```

4. وضع التجربة (معاينة فقط)

```bash
python3 copy_repo_files.py -c copy_config.json --dry-run
```

📖 شرح المعاملات (Arguments)

المعامل الاختصار الوصف
--source -s المستودع المصدر (مثال: Samo1408/Builder_kernel)
--branch -b اسم الفرع (الافتراضي: main)
--file -f مسار الملف المصدر داخل المستودع
--dest -d المسار الهدف لحفظ الملف
--config -c ملف JSON يحتوي على تكوين الملفات المتعددة
--force - فرض استبدال الملفات الموجودة
--dry-run - عرض ما سيتم نسخه بدون تحميل فعلي

📝 صيغة ملف JSON المتقدم

```json
{
    "source_repo": "Samo1408/Builder_kernel",
    "branch": "m32-new",
    "force": true,
    "files": [
        {
            "source": "fs/exec.c",
            "dest": "kernel_root/fs/exec.c"
        }
    ]
}
```

يمكنك أيضاً وضع force: true داخل ملف JSON لتفعيل الاستبدال الإجباري تلقائياً.

🎯 أمثلة عملية

مثال 1: تحضير ملفات الكيرنل للبناء

```bash
# إنشاء ملف تكوين kernel_files.json
cat > kernel_files.json << EOF
{
    "source_repo": "Samo1408/Builder_kernel",
    "branch": "m32-new",
    "files": [
        {"source": "fs/exec.c", "dest": "kernel/fs/exec.c"},
        {"source": "fs/open.c", "dest": "kernel/fs/open.c"},
        {"source": "fs/stat.c", "dest": "kernel/fs/stat.c"},
        {"source": "fs/read_write.c", "dest": "kernel/fs/read_write.c"},
        {"source": "kernel/reboot.c", "dest": "kernel/kernel/reboot.c"}
    ]
}
EOF

python3 copy_repo_files.py -c kernel_files.json --force
```

مثال 2: نسخ ملف من ريبو عام

```bash
python3 copy_repo_files.py -s torvalds/linux -b master -f Makefile -d ./my_kernel/Makefile
```

⚠️ ملاحظات مهمة

· الروابط تستخدم خدمة raw.githubusercontent.com
· الملفات العامة فقط (غير خاصة) يمكن الوصول إليها
· في حالة وجود ملف بنفس المسار الهدف، لن يتم استبداله إلا باستخدام --force
· يجب أن يكون المسار الهدف موجوداً (سيتم إنشاء المجلدات تلقائياً)

🐛 استكشاف الأخطاء وإصلاحها

المشكلة الحل
HTTP Error 404 تأكد من صحة المسار والفرع في المستودع المصدر
File exists استخدم --force لفرض الاستبدال
No module named '...' السكربت يعمل بمكتبات Python القياسية فقط
بطء في التحميل جرب تغيير رابط المستودع لـ HTTPS أو استخدام VPN

📄 الترخيص

MIT License - يمكنك استخدامه وتعديله بحرية.

🤝 المساهمة

في حال رغبتك في تحسين السكربت، يمكنك إضافة ميزات مثل:

· دعم المستودعات الخاصة (tokens)
· عرض شريط تقدم أثناء التحميل
· دعم نسخ مجلدات كاملة
· التحقق من صحة الملفات عبر Checksum

📞 الدعم

للاستفسارات أو المشاكل، يرجى فتح Issue أو التواصل عبر المنصة المستخدمة.

---










