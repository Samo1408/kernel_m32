🚀 أمثلة الاستخدام:

1. نسخ مجلد كامل:

```bash
python3 copy_github_folder.py -s Samo1408/Builder_kernel -b m32-new -t folder -f fs -d kernel_root/fs --force
```

2. نسخ ملف واحد:

```bash
python3 copy_github_folder.py -s Samo1408/Builder_kernel -b m32-new -t file -f build.sh -d build.sh --force
```

3. نسخ مجلدات متعددة باستخدام JSON:

```bash
python3 copy_github_folder.py -c folders_config.json --force
```

4. نسخ بدون subdirectories:

```bash
python3 copy_github_folder.py -s Samo1408/Builder_kernel -b m32-new -t folder -f fs -d kernel_root/fs --no-recursive
```




الميزات الجديدة في السكربت:

· ✅ نسخ مجلدات كاملة (مع كل المحتويات)
· ✅ الحفاظ على هيكل المجلدات (subdirectories)
· ✅ نسخ ملفات ومجلدات مختلطة
· ✅ تحكم في التعمق (recursive on/off)
· ✅ دمج الميزات مع JSON config
· ✅ عرض التقدم أثناء النسخ
· ✅ استخدام GitHub API لقراءة محتويات المجلدات

الفرق الأساسي عن السكربت القديم: السكربت الجديد بيستخدم GitHub API عشان يجيب ليستة كل الملفات في المجلد أولاً، وبعد كده ينزل كل ملف على حدة.




