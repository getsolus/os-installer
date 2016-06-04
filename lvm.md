**Create Physical Volume**

    new partition type lvm (flag)
    lvm pvcreate -M 2 /dev/sdb1

     ikey@solus-bdw  ~  sudo systemctl enable lvm2-lvmetad.socket 
    Created symlink from /etc/systemd/system/sysinit.target.wants/lvm2-lvmetad.socket to /usr/lib64/systemd/system/lvm2-lvmetad.socket.

     ikey@solus-bdw  ~  sudo systemctl start lvm2-lvmetad.socket 
     ikey@solus-bdw  ~  sudo pvscan                             
      PV /dev/sdb1                      lvm2 [465.76 GiB]
      Total: 1 [465.76 GiB] / in use: 0 [0   ] / in no VG: 1 [465.76 GiB]
     ikey@solus-bdw  ~ 
     
     ikey@solus-bdw  ~/bin  sudo vgcreate InstallRoot /dev/sdb1
      Volume group "InstallRoot" successfully created
     ikey@solus-bdw  ~/bin  

     ✘ ⚙ ikey@solus-bdw  ~/onetwo/os-installer   master  sudo lvcreate -n MineSwap  --size 4GB InstallRoot /dev/sdb1
      Logical volume "MineSwap" created.
     ⚙ ikey@solus-bdw  ~/onetwo/os-installer   master  

    sudo lvcreate -n MineRoot -l 100%FREE InstallRoot /dev/sdb1
      Logical volume "MineRoot" created.

     ⚙ ikey@solus-bdw  ~/onetwo/os-installer   master  sudo mkfs.ext4 /dev/InstallRoot/MineRoot 

     ikey@solus-bdw  ~/onetwo/os-installer   master  sudo vgchange -ay
      2 logical volume(s) in volume group "InstallRoot" now active
     ikey@solus-bdw  ~/onetwo/os-installer   master  

     ikey@solus-bdw  ~/onetwo/os-installer   master  sudo vgchange -an
      0 logical volume(s) in volume group "InstallRoot" now active
     ikey@solus-bdw  ~/onetwo/os-installer   master  
