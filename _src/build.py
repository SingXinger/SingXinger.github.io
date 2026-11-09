#!/usr/bin/env python3
"""Generate the multilingual promo pages from _src/template.ko.html.

Run from the repo root:  python3 _src/build.py
Outputs: index.html (ko), en/index.html, ja/index.html, zh-tw/index.html, zh-cn/index.html
The Toss (intoss://) button and Toss mentions exist only in the Korean page.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://singxinger.github.io"
tpl = open(os.path.join(ROOT, "_src/template.ko.html"), encoding="utf-8").read()

LANGS = [  # code, dir, html lang, og locale, switcher label
    ("ko", "", "ko", "ko_KR", "한국어"),
    ("en", "en/", "en", "en_US", "English"),
    ("ja", "ja/", "ja", "ja_JP", "日本語"),
    ("zh", "zh-tw/", "zh-Hant-TW", "zh_TW", "繁體中文"),
    ("zs", "zh-cn/", "zh-Hans-CN", "zh_CN", "简体中文"),
]
# Simplified Chinese copy: converted from the zh column (OpenCC tw2sp) and reviewed; ko text -> zh-Hans text
ZHS = json.load(open(os.path.join(ROOT, "_src/zhs.json"), encoding="utf-8"))
IMGDIR = {"en": "en", "ja": "ja", "zh": "zh", "zs": "zhcn"}

# (ko, en, ja, zh) -- ko must occur verbatim in the template.
T = [
 ("운기조식 — 오늘도 애썼으니, 숨 좀 돌려요",
  "Ungijosik — You worked hard today. Catch your breath.",
  "運気調息 — 今日もがんばったから、ひと息つこう",
  "運氣調息 — 今天也辛苦了,喘口氣吧"),
 ("호흡으로 기를 모으고, 나를 회복하는 무협 힐링 게임 운기조식. 게임 소개, 영상과 다운로드 안내.",
  "Ungijosik is a healing wuxia game: gather qi through your breath and recover yourself. Game intro, trailer and download info.",
  "呼吸で気を集め、自分を回復する武侠ヒーリングゲーム「運気調息」。ゲーム紹介、映像、ダウンロード案内。",
  "用呼吸聚氣、療癒自己的武俠療癒遊戲《運氣調息》。遊戲介紹、影片與下載資訊。"),
 ('aria-label="주요 메뉴"', 'aria-label="Main menu"', 'aria-label="メインメニュー"', 'aria-label="主選單"'),
 (">게임 소개<", ">About<", ">ゲーム紹介<", ">遊戲介紹<"),
 (">수련의 여정<", ">The Path<", ">修練の道<", ">修練之路<"),
 (">영상<", ">Trailer<", ">映像<", ">影片<"),
 (">만나는 방법 ↗<", ">Get the game ↗<", ">遊ぶ方法 ↗<", ">如何下載 ↗<"),
 ("무협의 세계에서 찾는, 나만의 쉼",
  "A rest of your own, in the world of wuxia",
  "武侠の世界で見つける、自分だけの休息",
  "在武俠世界裡,找到屬於自己的小憩"),
 ("오늘도 애썼으니,<br>게임에선<br><em>숨 좀 돌려요.</em>",
  "You worked hard today.<br>In the game,<br><em>just catch your breath.</em>",
  "今日もがんばったから、<br>ゲームの中では<br><em>ひと息つこう。</em>",
  "今天也辛苦了,<br>在遊戲裡<br><em>喘口氣吧。</em>"),
 ("호흡으로 기를 모으고,<br>다시 나아갈 힘을 되찾는 무협 힐링 게임.",
  "Gather qi with your breath<br>and find the strength to move forward again.<br>A healing wuxia game.",
  "呼吸で気を集め、<br>もう一度前へ進む力を取り戻す武侠ヒーリングゲーム。",
  "用呼吸聚氣,<br>找回再次前行的力量。武俠療癒遊戲。"),
 ('운기조식 만나기 <span>↗</span>', 'Play Ungijosik <span>↗</span>', '運気調息を遊ぶ <span>↗</span>', '開始《運氣調息》 <span>↗</span>'),
 ("▷ 홍보영상 보기", "▷ Watch the trailer", "▷ 紹介映像を見る", "▷ 觀看宣傳影片"),
 ('Google Play <span class="divider">/</span> 토스 미니앱 오픈', "Available on Google Play", "Google Play で配信中", "已於 Google Play 上架"),
 ('alt="운기조식 포스터. 숲속 정자에서 푸른 도복의 무림인이 운기조식하는 모습"',
  'alt="Ungijosik poster: a martial artist in a blue robe practising breathwork in a forest pavilion"',
  'alt="運気調息のポスター。森の東屋で青い道着の武林人が運気調息をする姿"',
  'alt="《運氣調息》海報:身穿青色道服的武林人士在森林涼亭中運氣調息"'),
 ("한 호흡, 다시 시작하는 힘.", "One breath, begin again.", "ひと息ごとに、また始める力。", "一口氣,重新開始的力量。"),
 ("아래로 천천히 <span>↓</span>", "Scroll slowly <span>↓</span>", "ゆっくり下へ <span>↓</span>", "慢慢往下 <span>↓</span>"),
 ("강해지는 일도,<br><span>숨을 고르는 데서 시작하니까.</span>",
  "Even getting stronger<br><span>begins with steadying your breath.</span>",
  "強くなることも、<br><span>息を整えるところから始まるから。</span>",
  "變強這件事,<br><span>也是從調勻呼吸開始。</span>"),
 ("쓰러진 뒤 다시 일어나는 무림인의 이야기.<br>작은 호흡을 쌓고, 막힌 기의 길을 열고,<br>어제보다 조금 더 오래 버티는 나를 만납니다.",
  "The story of a martial artist who rises after falling.<br>Stack small breaths, open the blocked paths of qi,<br>and meet a you who lasts a little longer than yesterday.",
  "倒れても、また立ち上がる武林人の物語。<br>小さな呼吸を積み重ね、塞がった気の道を開き、<br>昨日より少しだけ長く耐えられる自分に出会います。",
  "跌倒之後再次站起的武林人物語。<br>累積細小的呼吸,打通阻塞的氣脈,<br>遇見比昨天多撐一會兒的自己。"),
 ("나만의 속도로, 수련의 길.", "At your own pace, the path of cultivation.", "自分のペースで、修練の道。", "以自己的步調,走修練之路。"),
 ("한 번의 숨이 기가 되고,<br>차곡차곡 쌓인 기가 다음 걸음이 됩니다.",
  "One breath becomes qi,<br>and qi, steadily gathered, becomes your next step.",
  "ひと息が気になり、<br>積み重なった気が次の一歩になります。",
  "一口氣化為氣,<br>一點一滴累積的氣,成為下一步。"),
 ("01 / 호흡", "01 / Breath", "01 / 呼吸", "01 / 呼吸"),
 ("누르고, 놓고.<br>내 호흡에 집중하는 시간.", "Press, release.<br>Time to focus on your breath.", "押して、離して。<br>自分の呼吸に集中する時間。", "按住、放開。<br>專注於自己呼吸的時光。"),
 ("원이 커질 때 누르고, 작아질 때 놓으세요. 들숨과 날숨의 박자에 맞춰 단전에 기를 모읍니다.",
  "Press as the circle grows and release as it shrinks. Follow the rhythm of each inhale and exhale to gather qi in your dantian.",
  "円が大きくなるときに押し、小さくなるときに離します。吸う息と吐く息の拍に合わせて、丹田に気を集めます。",
  "圓圈變大時按住,變小時放開。配合吸氣與吐氣的節奏,在丹田聚集氣。"),
 ('alt="단전의 원에 맞춰 호흡하는 운기조식 실제 게임 화면"',
  'alt="Real Ungijosik gameplay: breathing in time with the dantian circle"',
  'alt="丹田の円に合わせて呼吸する、運気調息の実際のゲーム画面"',
  'alt="《運氣調息》實際遊戲畫面:配合丹田圓圈呼吸"'),
 ("02 / 경맥", "02 / Meridians", "02 / 経脈", "02 / 經脈"),
 ("막혀 있던 길에<br>다시 빛이 흐르도록.", "Let light flow again<br>through the blocked paths.", "塞がっていた道に、<br>もう一度光が流れるように。", "讓阻塞的道路,<br>再次流動光芒。"),
 ("호흡으로 모은 기를 이끌어 혈도를 하나씩 열어 보세요. 손끝을 따라 경맥에 새로운 길이 이어집니다.",
  "Guide the qi you gathered to open acupoints one by one. Following your fingertip, new paths connect along the meridians.",
  "呼吸で集めた気を導き、経穴をひとつずつ開いてみましょう。指先をたどって、経脈に新しい道がつながります。",
  "引導用呼吸聚集的氣,逐一打通穴道。順著指尖,經脈上將連起新的道路。"),
 ('alt="혈도를 여는 실제 게임 화면"', 'alt="Real gameplay: opening acupoints"', 'alt="経穴を開く実際のゲーム画面"', 'alt="實際遊戲畫面:打通穴道"'),
 ("03 / 무공", "03 / Martial arts", "03 / 武功", "03 / 武功"),
 ("작은 수련이 쌓여,<br>나만의 한 수가 되다.", "Small drills add up<br>to a move all your own.", "小さな修練が積み重なり、<br>自分だけの一手になる。", "小小的修練累積起來,<br>成為屬於自己的一招。"),
 ("금강장, 청풍검, 비연퇴. 초식의 박자를 익히고 무공을 연성하세요. 익힌 무공은 마인과의 대전에서 펼쳐집니다.",
  "Diamond Body, Wind Sword, Swallow Kick. Learn each technique's rhythm and train your martial arts. What you learn unfolds in your battles with the demon.",
  "金剛掌、青風剣、飛燕脚。技の拍を覚えて武功を磨きましょう。習得した武功は、魔人との対戦で繰り出されます。",
  "金剛掌、清風劍、飛燕腿。熟悉招式的節奏,修練武功。學會的武功會在與魔人的對戰中施展。"),
 ('alt="금강장으로 마인과 대전하는 실제 게임 화면"', 'alt="Real gameplay: battling the demon with Diamond Palm"', 'alt="金剛掌で魔人と対戦する実際のゲーム画面"', 'alt="實際遊戲畫面:以金剛掌與魔人對戰"'),
 ("실제 게임 화면 · 원화 재적용 및 화면 개선 후 캡처", "Real in-game screens · captured after the art and UI refresh", "実際のゲーム画面 · 原画の再適用と画面改善後にキャプチャ", "實際遊戲畫面 · 於原畫重新套用與畫面改善後擷取"),
 ("다시 마주할 때는,<br><em>조금 더 오래.</em>", "When we face it again,<br><em>a little longer.</em>", "再び向き合うときは、<br><em>少しだけ長く。</em>", "再次面對時,<br><em>多撐一會兒。</em>"),
 ("문파가 불타던 그날 이후,<br>동굴 속에서 홀로 시작한 운기조식.<br><br>모은 내공과 익힌 무공으로 마인 앞에 다시 섭니다.<br>쓰러져도 괜찮습니다. 다시 숨을 고르면 되니까요.",
  "Ever since the day the sect burned,<br>you began your breathwork alone in a cave.<br><br>With the qi you gathered and the arts you learned, you stand before the demon again.<br>It's okay to fall. You just steady your breath once more.",
  "門派が燃えたあの日から、<br>洞窟の中でひとり始めた運気調息。<br><br>集めた内功と習得した武功で、もう一度魔人の前に立ちます。<br>倒れても大丈夫。また息を整えればいいのだから。",
  "自從門派焚毀的那一天,<br>在洞窟中獨自展開的運氣調息。<br><br>憑著累積的內功與學會的武功,再次站到魔人面前。<br>跌倒也沒關係。再調勻呼吸就好。"),
 ("게임 속 풍경 둘러보기 ↓", "Look around the game ↓", "ゲームの風景を見る ↓", "瀏覽遊戲場景 ↓"),
 ('alt="문파가 불타던 날을 보여 주는 게임 속 도트 만화"', 'alt="In-game pixel comic showing the day the sect burned"', 'alt="門派が燃えた日を描くゲーム内のドット絵マンガ"', 'alt="遊戲內像素漫畫:門派焚毀的那一天"'),
 ("잠시, 운기조식의 세계로.", "For a moment, step into the world of Ungijosik.", "しばし、運気調息の世界へ。", "暫時,走進《運氣調息》的世界。"),
 ("<p>홍보영상</p>", "<p>Trailer</p>", "<p>紹介映像</p>", "<p>宣傳影片</p>"),
 ('title="운기조식 홍보영상"', 'title="Ungijosik trailer"', 'title="運気調息 紹介映像"', 'title="《運氣調息》宣傳影片"'),
 ("YouTube에서 보기 ↗", "Watch on YouTube ↗", "YouTube で見る ↗", "在 YouTube 上觀看 ↗"),
 ("고요한 수련, 깊어지는 이야기.", "Quiet training, a deepening story.", "静かな修練、深まる物語。", "靜謐的修練,漸深的故事。"),
 ("이미지를 누르면 크게 볼 수 있습니다.", "Tap an image to enlarge it.", "画像をタップすると大きく表示されます。", "點擊圖片可放大檢視。"),
 ("호흡 · 기를 모으는 시간", "Breath · Time to gather qi", "呼吸 · 気を集める時間", "呼吸 · 聚氣的時光"),
 ("혈도 · 막힌 길을 열다", "Acupoints · Opening the blocked path", "経穴 · 塞がった道を開く", "穴道 · 打通阻塞之路"),
 ("대전 · 금강장의 일격", "Battle · A strike of Diamond Palm", "対戦 · 金剛掌の一撃", "對戰 · 金剛掌一擊"),
 ("컷신 · 마인의 신공", "Cutscene · The demon's secret art", "カットシーン · 魔人の神功", "過場 · 魔人的神功"),
 ("기연 · 길 잃은 노의원", "Encounter · The lost old physician", "奇縁 · 道に迷った老医師", "奇遇 · 迷路的老醫者"),
 ("크게 보기", "enlarge", "拡大表示", "放大檢視"),
 ("오늘의 수련은,<br><em>편안한 한 호흡부터.</em>", "Today's training starts<br><em>with one easy breath.</em>", "今日の修練は、<br><em>楽なひと息から。</em>", "今天的修練,<br><em>從輕鬆的一口氣開始。</em>"),
 ("운기조식을 만나는 방법을 안내합니다.", "Here's how to play Ungijosik.", "運気調息の遊び方をご案内します。", "說明如何下載《運氣調息》。"),
   ("Google Play와 토스 미니앱으로 만나보세요.<br>토스 미니앱은 휴대폰에 토스 앱이 설치된 기기에서 열립니다.",
  "Available now on Google Play.",
  "Google Play で配信中です。",
  "現已於 Google Play 上架。"),
 ("시작하기 전에.", "Before you begin.", "始める前に。", "開始之前。"),
 ("어떤 게임인가요?", "What kind of game is it?", "どんなゲームですか?", "這是什麼樣的遊戲?"),
 ("호흡으로 기를 모으고, 혈도를 열고, 무공을 수련하는 도트 무협 게임입니다. 쌓은 내공과 무공으로 마인과의 대전에 도전합니다.",
  "A pixel wuxia game where you gather qi through breathing, open acupoints and train martial arts. You take on the demon with the qi and arts you have built up.",
  "呼吸で気を集め、経穴を開き、武功を修練するドット絵の武侠ゲームです。積み上げた内功と武功で、魔人との対戦に挑みます。",
  "以呼吸聚氣、打通穴道、修練武功的像素風武俠遊戲。憑著累積的內功與武功,挑戰與魔人的對戰。"),
 ("어떻게 조작하나요?", "How do I play?", "操作方法は?", "怎麼操作?"),
 ("호흡의 원이 커질 때 누르고 작아질 때 놓아 들숨과 날숨을 이어 갑니다. 무공은 초식의 박자에 맞춰 연성하며, 대전은 자동으로 진행됩니다.",
  "Press as the breathing circle grows and release as it shrinks to chain your inhales and exhales. Train martial arts to each technique's rhythm; battles play out automatically.",
  "呼吸の円が大きくなるときに押し、小さくなるときに離して、吸う息と吐く息をつなげます。武功は技の拍に合わせて修練し、対戦は自動で進みます。",
  "呼吸圓圈變大時按住、變小時放開,接續每一次吸氣與吐氣。武功配合招式的節奏修練,對戰則自動進行。"),
 ("지금 다운로드할 수 있나요?", "Can I download it now?", "今すぐダウンロードできますか?", "現在可以下載嗎?"),
 ('네. Android에서는 <a class="text-link" href="https://play.google.com/store/apps/details?id=com.ungijosik.game" target="_blank" rel="noopener noreferrer">Google Play</a>에서 받을 수 있고, 토스 앱에서는 <a class="text-link" href="intoss://ungijosik">토스 미니앱으로 열기</a>로 바로 만날 수 있습니다.',
  'Yes. On Android, get it on <a class="text-link" href="https://play.google.com/store/apps/details?id=com.ungijosik.game" target="_blank" rel="noopener noreferrer">Google Play</a>.',
  'はい。Android では <a class="text-link" href="https://play.google.com/store/apps/details?id=com.ungijosik.game" target="_blank" rel="noopener noreferrer">Google Play</a> から入手できます。',
  '可以。Android 裝置可從 <a class="text-link" href="https://play.google.com/store/apps/details?id=com.ungijosik.game" target="_blank" rel="noopener noreferrer">Google Play</a> 下載。'),
 ("한 호흡에서 시작되는 무림.", "A martial world that begins with one breath.", "ひと息から始まる武林。", "從一口氣開始的武林。"),
 ('aria-label="이미지 닫기"', 'aria-label="Close image"', 'aria-label="画像を閉じる"', 'aria-label="關閉圖片"'),
 ('alt="확대된 게임 화면"', 'alt="Enlarged game screen"', 'alt="拡大したゲーム画面"', 'alt="放大的遊戲畫面"'),
 ("개인정보처리방침", "Privacy Policy", "プライバシーポリシー", "隱私權政策"),
 (" · 문의 ", " · Contact ", " · お問い合わせ ", " · 聯絡 "),
 ("맨 위로 ↑", "Back to top ↑", "ページ上部へ ↑", "回到頂端 ↑"),
]

BRAND = {"en": "Ungijosik", "ja": "運気調息", "zh": "運氣調息", "zs": "运气调息"}
FONTS = {
 "ko": None,
 "en": "https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&family=Noto+Serif:wght@500;600;700&display=swap",
 "ja": "https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700&display=swap",
 "zh": "https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Serif+TC:wght@500;600;700&display=swap",
 "zs": "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=Noto+Serif+SC:wght@500;600;700&display=swap",
}
FAMS = {"en": ("Noto Sans", "Noto Serif"), "ja": ("Noto Sans JP", "Noto Serif JP"), "zh": ("Noto Sans TC", "Noto Serif TC"), "zs": ("Noto Sans SC", "Noto Serif SC")}
EXTRA_CSS = {
 "en": ".hero h1{font-size:clamp(32px,3.9vw,56px);letter-spacing:-1px;line-height:1.25}h2{letter-spacing:-.5px}.eyebrow{letter-spacing:2px}@media(max-width:760px){.hero h1{font-size:34px;letter-spacing:-.5px}}",
 "ja": ".hero h1{letter-spacing:-1px;line-height:1.4}h2{letter-spacing:0}@media(max-width:760px){.hero h1{font-size:36px;letter-spacing:-.5px}}",
 "zh": ".hero h1{letter-spacing:0;line-height:1.4}h2{letter-spacing:0}@media(max-width:760px){.hero h1{font-size:38px;letter-spacing:0}}",
 "zs": ".hero h1{letter-spacing:0;line-height:1.4}h2{letter-spacing:0}@media(max-width:760px){.hero h1{font-size:38px;letter-spacing:0}}",
}
SWITCH_CSS = (".lang{display:flex;gap:14px;font-size:11px;color:var(--muted);white-space:nowrap}"
              ".lang a{padding:4px 0;border-bottom:1px solid transparent}.lang a[aria-current]{color:var(--mint);border-color:#536f5e}"
              ".lang a:hover{color:var(--ink)}.head-right{display:flex;align-items:center;gap:22px}"
              "@media(max-width:760px){.head-right{gap:10px;flex-direction:column;align-items:flex-end}.lang{gap:9px;font-size:10px}}")

assert len(set(t[0] for t in T)) == len(T)
for t in T:
    assert t[0] in tpl, "missing in template: " + t[0][:40]


def build(idx):
    code, d, htmllang, og, _ = LANGS[idx]
    out = tpl
    if code != "ko":
        col = {"en": 1, "ja": 2, "zh": 3}.get(code)
        # longest ko strings first so substrings never pre-empt longer ones
        for row in sorted(T, key=lambda r: -len(r[0])):
            out = out.replace(row[0], ZHS[row[0]] if code == "zs" else row[col])
        out = out.replace('>운기조식<span', '>' + BRAND[code] + '<span')
        # language-specific copies of the game/poster images (text baked in)
        out = re.sub(r'/img/([0-9a-f]{8})\.webp', lambda m: '/img/%s/%s.webp' % (IMGDIR[code], m.group(1)), out)
        gp = {"en": ("en.svg", "Get it on Google Play"), "ja": ("ja.png", "Google Play で手に入れよう"),
              "zh": ("zh-tw.svg", "在 Google Play 上取得"), "zs": ("zh-cn.svg", "在 Google Play 上获取")}[code]
        out = out.replace('/img/gplay/ko.svg', '/img/gplay/' + gp[0], 1).replace('alt="Google Play에서 다운로드"', 'alt="%s"' % gp[1], 1)
        # drop the Toss card (Korean-only)
        out, n = re.subn(r'<a class="toss-badge" href="intoss://ungijosik">.*?</a>(?=</div>)', "", out, flags=re.S)
        assert n == 1, "toss card not found"
        out = out.replace('.toss-badge{display:block;width:200px;max-width:100%;margin:0 auto;align-self:center}.toss-badge img{display:block;width:100%;height:auto}', '', 1)
        out = out.replace('<div class="platforms">', '<div class="platforms one">', 1)
        out = out.replace(".platforms .play-link{", ".platforms.one{grid-template-columns:minmax(0,420px);justify-content:center}.platforms .play-link{", 1)
        # fonts
        out = out.replace("@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;900&family=Noto+Serif+KR:wght@500;600;700&display=swap');",
                          "@import url('%s');" % FONTS[code], 1)
        sans, serif = FAMS[code]
        out = out.replace("'Noto Sans KR'", "'%s'" % sans).replace("'Noto Serif KR'", "'%s'" % serif)
        out = out.replace("</style>", EXTRA_CSS[code] + "</style>", 1)
        assert "intoss" not in out and "토스" not in out
    out = out.replace('<html lang="ko">', '<html lang="%s">' % htmllang, 1)
    out = out.replace("</style>", SWITCH_CSS + "</style>", 1)
    # language switcher + head links
    here = "/" + d
    sw = '<div class="lang" aria-label="Language">' + "".join(
        '<a href="/%s" hreflang="%s" lang="%s"%s>%s</a>' % (l[1], l[2], l[2], ' aria-current="true"' if l[0] == code else "", l[4])
        for l in LANGS) + "</div>"
    out = re.sub(r'(<a class="nav-cta"[^>]*>.*?</a>)', r'<div class="head-right">\1' + sw + "</div>", out, count=1, flags=re.S)
    title = re.search(r"<title>(.*?)</title>", out).group(1)
    desc = re.search(r'<meta name="description" content="(.*?)">', out).group(1)
    links = "".join('<link rel="alternate" hreflang="%s" href="%s/%s">' % (l[2], SITE, l[1]) for l in LANGS)
    links += '<link rel="alternate" hreflang="x-default" href="%s/">' % SITE
    links += '<link rel="canonical" href="%s%s">' % (SITE, here)
    links += ('<meta property="og:type" content="website"><meta property="og:title" content="%s">'
              '<meta property="og:description" content="%s"><meta property="og:locale" content="%s">'
              '<meta property="og:url" content="%s%s"><meta property="og:image" content="%s/img/og.jpg">'
              '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
              '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="%s/img/og.jpg">') % (title, desc, og, SITE, here, SITE, SITE)
    out = out.replace("</title>", "</title>" + links, 1)
    path = os.path.join(ROOT, d, "index.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(out)
    print(path, len(out))


for i in range(len(LANGS)):
    build(i)


# sitemap.xml + robots.txt
urls = "".join(
    "<url><loc>%s/%s</loc>%s</url>" % (SITE, l[1], "".join(
        '<xhtml:link rel="alternate" hreflang="%s" href="%s/%s"/>' % (m[2], SITE, m[1]) for m in LANGS))
    for l in LANGS)
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + urls + "</urlset>")
open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(
    "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)
