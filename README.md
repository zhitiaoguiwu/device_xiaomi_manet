- 该设备树使用方法（大概方法与注意事项）
- 首先需要把本设备树与sm8650设备树， 内核文件（manet-kernel）拉进lineageos源码device/xiaomi/目录下
- vendor目录同理，也可以由设备树的extract-files.py来生成（底包OS3.0.305.0.WNMCNXM）,用payload-dumper获取镜像。然后就是用dumpyara解包卡刷包，获取blobs，将获取的镜像与解包文件塞进一个文件夹里（sm8650与manet设备树均要获取）
- 注意los的相机目前由miuicamera代替(不要尝试去维护los相机，除非你能修好)
- 编译请在源码目录执行：
source build/envsetup.sh
lunch lineage_manet-bp4a-userdebug
m bacon
