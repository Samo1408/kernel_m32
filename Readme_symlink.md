مثال لملف JSON Config (symlinks.json):

```json
{
    "use_relative": true,
    "symlinks": [
        {
            "target": "../../KernelSU-Next/kernel",
            "link": "kernel_root/drivers/kernelsu",
            "relative": true
        },
        {
            "target": "../../Builder_kernel/fs",
            "link": "kernel_root/fs",
            "relative": true
        },
        {
            "target": "../../Builder_kernel/kernel",
            "link": "kernel_root/kernel",
            "relative": true
        }
    ]
}
```

🚀 أمثلة الاستخدام:

1. إنشاء symlink واحد:

```bash
python3 symlink_creator.py -t ../../KernelSU-Next/kernel -l kernel_root/drivers/kernelsu
```

2. إنشاء symlink مع فرض الاستبدال:

```bash
python3 symlink_creator.py -t ../../KernelSU-Next/kernel -l kernel_root/drivers/kernelsu --force
```

3. استخدام مسار مطلق (بدل النسبي):

```bash
python3 symlink_creator.py -t /home/user/KernelSU-Next/kernel -l kernel_root/drivers/kernelsu --absolute
```

4. إنشاء عدة symlinks مرة واحدة:

```bash
python3 symlink_creator.py -m "../../KernelSU-Next/kernel:kernel_root/drivers/kernelsu" "../../Builder_kernel/fs:kernel_root/fs" "../../Builder_kernel/kernel:kernel_root/kernel"
```

5. استخدام JSON config:

```bash
python3 symlink_creator.py -c symlinks.json --force
```

6. تجربة (Dry run) من غير تنفيذ:

```bash
python3 symlink_creator.py -t ../../KernelSU-Next/kernel -l kernel_root/drivers/kernelsu --dry-run
```

لحالتك المحددة (KernelSU-Next):

```bash
# اتأكد إنك داخل مجلد Builder_kernel
cd /home/runner/work/Builder_kernel/Builder_kernel

# اعمل الـ symlink
python3 symlink_creator.py -t KernelSU-Next/kernel -l kernel_root/drivers/kernelsu --force
```

الميزات:

· ✅ يدعم المسارات النسبية (الافتراضي) والمطلقة
· ✅ فرض الاستبدال للملفات الموجودة (--force)
· ✅ وضع التجربة (--dry-run) للمعاينة
· ✅ دعم JSON config للمشاريع الكبيرة
· ✅ معالجة الأخطاء مع رسائل واضحة
· ✅ إنشاء المجلدات الأب تلقائياً
· ✅ إنشاء عدة symlinks دفعة واحدة