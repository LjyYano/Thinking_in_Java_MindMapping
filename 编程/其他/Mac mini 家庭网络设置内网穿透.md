# 前言

在拼多多上花 2899 块钱买了一个 M4 16G 256G 的 Mac Mini，因为手里本来有一个对外提供的 web 服务，还为此买了阿里云 ECS 和 云数据库，就想把这个当成一个服务器。

# 整体步骤

- [ ]  向运营商索要家庭宽带的公网 IP
- [ ]  光猫改成桥接模式
- [ ]  为 Mac mini 分配固定的局域网 IP
- [ ]  Mac mini 设置、加固
- [ ]  路由器做端口映射
- [ ]  内网穿透

## 向运营商索要家庭宽带的公网IP

检查自己家的网络是否是 10.x.x.x、100.64.x.x、192.168.x.x 这类保留网段，说明被运营商 NAT 或 CG‑NAT，并不是真正的独享公网 IP——此时就算做端口映射也无法从外网直连，需要穿透方案（Tailscale / frp 等）。

### 检查自己是否是公网方案 1：命令行

最简单的方案，通过命令行获取：

```bash
curl -4 ifconfig.co
```

- 加 -4 强制获取 IPv4；想看 IPv6 则 curl -6 ifconfig.co。
- 还可以用 curl https://api.ipify.org 或 curl https://ipinfo.io/ip，效果相同。

动态公网 IP：运营商可能在断电、重新拨号、乃至定期轮换时给你新的 IP。若想域名永久指向家里，需要 DDNS 客户端 每隔几分钟检测并更新。

如果不是动态公网IP，需要拨打运营商电话让其开通。动态公网IP是免费的，静态公网IP是要花钱的，大概每个月100块钱。动态公网IP虽然会变，但是配合域名或免费的ddns等方案能够实现和静态公网IP一样的效果。

### 检查自己是否是公网方案 2：打开路由器设置

也可以打开路由器或光猫的设置界面，一般是 [http://192.168.](http://192.168.31.1/)1.1，看互联网的 IPv4 地址。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-05-23-18-33-30.png)

## 光猫改成桥接模式

我的宽带光猫并不是桥接模式，在设置的过程中光猫和路由器都要进行nat。但是最终发现如果光猫不是桥接模式的话，双层nat非常麻烦，而且运营商会把端口阉割，导致无法进行内网穿透。需要打电话给联通客服，让其更改，肯定是会给改的。

1. **确认宽带接入方式**
    - 如果 ISP 给的是 **PPPoE 用户名 / 密码**，把它填到小米路由器的 **上网设置 → 拨号上网 (PPPoE)**。
    - 光猫改成 **桥接 (Bridge) 模式**，或者找运营商客服把光猫改桥接。
2. 路由器重新拨号后，**WAN IP** 应变成 `111.194.140.*` 这类公网地址。
3. 之前做的 **外 3333 → 内 22** 映射立即生效，外网 `ssh -p 3333 user@<新公网 IP>` 就能连。

> 优点：只有一层 NAT，最干净；端口映射、 DDNS 都在小米路由器里完成。
> 
> 
> **缺点**：需要光猫支持桥接；部分运营商可能不提供拨号账号，需联系客服申请。
> 

### 为 Mac mini 分配固定的局域网 IP

1 · 在 Mac mini 上开启 SSH 服务

| 操作 | 说明 |
| --- | --- |
| **系统设置界面** |  > 系统设置 > 通用 > 共享 > 打开 **远程登录 (Remote Login)**，勾选 *仅允许下列用户* 并添加自己的账号。 |
| **终端命令** | `sudo systemsetup -setremotelogin on` （和图形界面作用相同） |

> 检查端口：执行 sudo lsof -iTCP:22 -sTCP:LISTEN，若能看到 sshd 进程，说明 22 端口已监听。
> 

2 · 给 Mac mini 分配固定的局域网 IP

1. 进入路由器后台，找到 **DHCP 静态绑定 / 地址保留**。
2. 记录 Mac mini 的 **MAC address**，将其绑定到如 `192.168.1.100`。
3. 重新获取地址或重启以生效。

> 固定内网 IP 能确保端口映射永远指向同一台机器。
> 

---

3 · 在路由器上做端口映射 (Port Forwarding)

| 选项 | 建议 |
| --- | --- |
| **外部端口 (WAN)** | 若 ISP 不屏蔽 22，可直接用 22；否则可改成 2222 或其他高位端口。 |
| **内部 IP** | 你的 Mac mini 内网地址，例如 `192.168.1.100`。 |
| **内部端口 (LAN)** | 22 （Mac mini 上 sshd 默认端口）。 |

保存后，路由器会把来自公网 `<家庭公网 IP>:外部端口` 的流量转发到 Mac mini 的 22 端口。

## Mac mini 设置、加固（必做）

- **只用密钥登录**
    
    ```bash
    bash
    复制编辑
    # 在本地电脑生成密钥
    ssh-keygen -t ed25519 -C "your_email@example.com"
    
    # 把公钥拷到 Mac mini
    ssh-copy-id -p 22 user@ssh.example.com
    
    ```
    
- **禁用密码登录、限制用户**
    
    编辑 `/etc/ssh/sshd_config`：
    
    ```
    conf
    复制编辑
    PermitRootLogin no
    PasswordAuthentication no
    AllowUsers your_user_name
    Port 22            # 如改用 2222，记得同步修改
    
    ```
    
    保存后 `sudo launchctl stop com.openssh.sshd && sudo launchctl start com.openssh.sshd` 重载配置。
    
- **安装防暴力工具**
    
    ```bash
    bash
    复制编辑
    brew install sshguard     # fail2ban 的 macOS 替代品
    sudo brew services start sshguard
    
    ```
    
- **定期打补丁**
    
    `softwareupdate --all --install --restart`
    

## 路由器做端口映射

在路由器里设置，如下图所示。我将 Mac mini 的内部 ip 地址固定设置成了 192.168.31.100，对外部的 2222 端口映射到内部的 ssh 22 端口；同时也设置了范围转发规则列表。

每个路由器页面可能有差距，但是这些功能基本都是有的。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-05-23-18-34-24.png)

## 内网穿透

说明：其实这里不是必须的，现在已经有了一个动态的公网 IP 地址，只是在路由器重启等情况下会自动分配新的地址。如果只是个人使用，直接拿公网 IP 地址或者免费的 DDNS 提供商即可。不过免费的 DDNS 国内好用的不多，我也没有实际使用过，走国外服务器代理的话速度太慢且不能自定义，就放弃了。

我是在阿里云官网购买了一个 .top 域名，180 块钱 10 年。之后就是在官网配置记录，比如申请的域名是 abc.top，配置一个主机记录 ai，即可访问 ai.abc.top。配置官方文档已经很详细了。

![](http://yano.oss-cn-beijing.aliyuncs.com/blog/2025-05-23-18-34-40.png)

在配置好后，就可以使用域名访问了，还要解决最后一个问题：这里配置的记录值 IP 是固定的，但是我们是动态公网 IP，是会变化的。所以需要在 mac 上使用 aliyun-ddns 脚本，这个脚本会自动检测 mac 本机的 IP 地址是否变化，如果有变化就更新上面截图中的域名主机记录。

aliyun-ddns 的 github 链接：https://github.com/risfeng/aliyun-ddns-shell。官方 [README.md](http://README.md) 非常详细了，本文不再赘述。

# 说明

这样就能够通过域名在任意地点、任意网络访问家里的 mac 了，可以当成一个服务器来使用。