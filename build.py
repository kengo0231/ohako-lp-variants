#!/usr/bin/env python3
"""OHAKO LP 訴求×導線のテスト用に、既存LP(base/ = ohako-self-lp)からFV・CTA・料金/時間の文言を差し替えた派生版を生成する。
使い方: python3 build.py  →  {slug}/index.html と index.html(一覧)を出力。css/img/legal/privacy は base から共有。
"""
import os, re, shutil, html

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = open(os.path.join(ROOT, 'base', 'index.html'), encoding='utf-8').read()

LINE_URL = 'https://s.lmes.jp/landing-qr/2008844403-6XdTkSMm?uLand=hKe9eZ'   # 全LINE版共通(訴求ごとに分ける場合は variants の line_url を変更)
BOOK_8H = 'https://ohako-beautyresort.com/book/nasu/'
BOOK_4H = 'https://ohako-beautyresort.com/book/nasu/4h/'
BOOK_FAC = {  # 施設一覧の「この施設を予約する」リンク
    '8h': {'OHAKO 那須塩原': 'https://ohako-beautyresort.com/book/nasu/', 'OHAKO つくば': 'https://ohako-beautyresort.com/book/tsukuba/'},
    '4h': {'OHAKO 那須塩原': 'https://ohako-beautyresort.com/book/nasu/4h/', 'OHAKO つくば': 'https://ohako-beautyresort.com/book/tsukuba/4h/'},
}

VARIANTS = [
    {'slug': 'beauty-line',   'appeal': 'beauty',   'cta': 'line', 'plan': '4h', 'label': '美容×サウナ×BBQ',                         'cta_label': 'LINE',   'plan_label': '1枠4時間', 'price_label': '1名16,500円'},
    {'slug': 'beauty-book',   'appeal': 'beauty',   'cta': 'book', 'plan': '4h', 'label': '美容×サウナ×BBQ',                         'cta_label': '予約ページ', 'plan_label': '1枠4時間', 'price_label': '1名16,500円'},
    {'slug': 'oneday-line',   'appeal': 'oneday',   'cta': 'line', 'plan': '8h', 'label': '送迎付きセルフエステ with サウナ、BBQ、焚き火', 'cta_label': 'LINE',   'plan_label': '1枠8時間', 'price_label': '1名2万円'},
    {'slug': 'oneday-book',   'appeal': 'oneday',   'cta': 'book', 'plan': '8h', 'label': '送迎付きセルフエステ with サウナ、BBQ、焚き火', 'cta_label': '予約ページ', 'plan_label': '1枠8時間', 'price_label': '1名2万円'},
    {'slug': 'machines-line', 'appeal': 'machines', 'cta': 'line', 'plan': '8h', 'label': 'マシン11種類も使える',                        'cta_label': 'LINE',   'plan_label': '1枠8時間', 'price_label': '1名2万円'},
    {'slug': 'machines-book', 'appeal': 'machines', 'cta': 'book', 'plan': '8h', 'label': 'マシン11種類も使える',                        'cta_label': '予約ページ', 'plan_label': '1枠8時間', 'price_label': '1名2万円'},
    {'slug': 'big3-nasu-book', 'appeal': 'big3',   'cta': 'book', 'plan': '4h', 'label': '最高級の3大マシン(風・森・大地)×貸切セルフエステ・那須塩原', 'cta_label': '予約ページ', 'plan_label': '1枠4時間', 'price_label': '1名16,500円'},
]

def rep(s, a, b, count=0, must=True):
    if must and a not in s:
        raise SystemExit('NOT FOUND: ' + a[:80])
    return s.replace(a, b) if count == 0 else s.replace(a, b, count)

# ------------------------------------------------------------------ FV(訴求ごと)
FV_START = '    <p class="fv__area">'
FV_END_MARK = '    <p class="fv__small">'
def fv_block(appeal, plan, cta_html):
    if appeal == 'beauty':
        return None  # 既存のまま
    if appeal == 'big3':
        area = 'OHAKO 那須塩原|完全貸切のセルフエステ'
        catch = '最高級のマシンで過ごす、<br>貸切セルフエステ。'
        benefit = '顔も、身体も、骨盤底筋も。<br>3台×11種類を、4時間貸切で自分のペースで。'
        gets = ['<li><em>風 KAZE</em>｜RFでフェイス・ボディ</li>', '<li><em>森 MORI</em>｜7ヘッドのボディケア</li>',
                '<li><em>大地 DAICHI</em>｜座って骨盤底筋ケア</li>', '<li><em>薪サウナ・水風呂・露天風呂</em>｜ととのう</li>', '<li><em>焚火ラウンジ</em>｜約30坪を貸切で</li>']
        return ('    <p class="fv__area">%s</p>\n    <h1 class="fv__catch">%s</h1>\n    <p class="fv__benefit">%s</p>\n    <ul class="fv__gets">\n%s\n    </ul>\n'
                '    <div class="fv__badge">\n      <span class="fv__badge-inc"><em>ぜんぶ込み</em>で4時間貸切</span>\n      <span class="fv__badge-now">1人 <em>16,500</em>円</span>\n    </div>\n%s'
                '    <p class="fv__small">1時間あたり4,125円(1名・4時間)|料金はお1人様あたり・一律|最大6名</p>\n') % (area, catch, benefit, '\n'.join('      ' + g for g in gets), cta_html)
    if appeal == 'oneday':
        area = 'OHAKO|送迎付き・1日貸切のセルフエステ'
        catch = '送迎付きの、<br>セルフエステ。<br>サウナも、BBQも、焚火も。'
        benefit = '非日常を体験しながら、<br>キレイになる1日。'
        gets = ['<li><em>痩身エステ</em>｜脂肪・セルライトへ</li>', '<li><em>小顔ケア</em>｜表情筋を動かす</li>',
                '<li><em>薪サウナ・水風呂</em>｜ととのう</li>', '<li><em>焚火・BBQ</em>｜森の一棟を貸切で</li>', '<li><em>駅から送迎</em>｜無料・要予約</li>']
    else:  # machines
        area = 'OHAKO|完全セルフ型 美容・コンディショニング施設'
        catch = '美容マシン、<br>11種類。<br>ぜんぶ使い放題。'
        benefit = 'サロンのマシンを、自分のペースで。<br>サウナも、焚火も、1日まるごと。'
        gets = ['<li><em>美容マシン11種類</em>｜回数・順番は自由</li>', '<li><em>痩身エステ・小顔ケア</em>｜好きなだけ</li>',
                '<li><em>薪サウナ・水風呂</em>｜ととのう</li>', '<li><em>焚火・BBQ・送迎</em>｜ぜんぶ込み</li>']
    badge_inc = '<em>ぜんぶ込み</em>で8時間貸切'
    badge_now = '1人 <em>20,000</em>円'
    small = '料金はお1人様あたり(平日18,000円)|2名〜6名|10:00〜18:00'
    return ('    <p class="fv__area">%s</p>\n    <h1 class="fv__catch">%s</h1>\n    <p class="fv__benefit">%s</p>\n    <ul class="fv__gets">\n%s\n    </ul>\n'
            '    <div class="fv__badge">\n      <span class="fv__badge-inc">%s</span>\n      <span class="fv__badge-now">%s</span>\n    </div>\n%s'
            '    <p class="fv__small">%s</p>\n') % (area, catch, benefit, '\n'.join('      ' + g for g in gets), badge_inc, badge_now, cta_html, small)

# ------------------------------------------------------------------ 8時間・2万円版の本文差し替え
TIMELINE_8H = '''    <div class="timeline">
      <h3 class="timeline__title">1日の過ごし方(例)</h3>
      <dl>
        <div><dt>9:45</dt><dd>駅で送迎車に乗車(無料・要予約)</dd></div>
        <div><dt>10:00</dt><dd>到着・使い方のご案内</dd></div>
        <div><dt>10:20</dt><dd>美容マシン 1周目(3台を交代で)</dd></div>
        <div><dt>12:00</dt><dd>薪サウナと水風呂で、ととのう</dd></div>
        <div><dt>13:00</dt><dd>焚火ラウンジでBBQ</dd></div>
        <div><dt>14:30</dt><dd>美容マシン 2周目</dd></div>
        <div><dt>16:00</dt><dd>露天風呂と外気浴</dd></div>
        <div><dt>18:00</dt><dd>送迎車で駅へ</dd></div>
      </dl>
      <p class="timeline__note">複数名なら、マシンは交代で。BBQの器材はあり、食材は持込またはオプション。</p>
    </div>'''

def apply_8h(s):
    s = rep(s, '<title>OHAKO|痩身も小顔もサウナも、4時間ぜんぶ込みで16,500円（那須塩原・つくば・成田）</title>',
            '<title>OHAKO|美容マシンもサウナも焚火も、送迎付き8時間ぜんぶ込みで1人20,000円（那須塩原・つくば）</title>')
    s = rep(s, '<h3><span>価値 01</span>4時間、完全貸切</h3>', '<h3><span>価値 01</span>8時間、完全貸切(10〜18時)</h3>')
    s = rep(s, '          <li>焚火ラウンジ(映画・BBQ)</li>\n          <li>くつろぎのリビング</li>',
            '          <li>焚火ラウンジ・BBQ器材</li>\n          <li>くつろぎのリビング</li>\n          <li>駅からの送迎(無料・要予約)</li>')
    s = rep(s, '<p class="whatis__punch">これ全部で、<strong>1人16,500円。</strong></p>', '<p class="whatis__punch">これ全部で、<strong>1人20,000円。</strong></p>')
    s = rep(s, '<p class="compare__price">1人 <em>16,500</em>円</p>', '<p class="compare__price">1人 <em>20,000</em>円</p>')
    s = rep(s, '<p class="cycle__punch">この流れを、<strong>4時間まるごと、自分のペースで。</strong></p>', '<p class="cycle__punch">この流れを、<strong>8時間まるごと、自分のペースで。</strong></p>')
    s = rep(s, '<h2 class="sec__title">この4時間で、<br>手に入るもの。</h2>', '<h2 class="sec__title">この8時間で、<br>手に入るもの。</h2>')
    s = rep(s, 'その「できていない」が、4時間でまとめて片づきます。', 'その「できていない」が、8時間でまとめて片づきます。')
    s = rep(s, '<p class="gets__punch-2">4時間、<em>16,500円</em>で。</p>', '<p class="gets__punch-2">8時間、<em>20,000円</em>で。</p>')
    s = rep(s, '<p class="sec__body">サウナも、焚火も、映画も。<br>誰にも気を使わない4時間。</p>', '<p class="sec__body">サウナも、焚火も、BBQも。<br>誰にも気を使わない8時間。</p>')
    s = re.sub(r'    <div class="timeline">.*?    </div>', TIMELINE_8H, s, count=1, flags=re.S)
    s = rep(s, '<h3>1棟1日2組までの、2部制</h3>\n        <p>10-14時と16-20時の2枠のみ。ムダのない運営で価格を抑えています。</p>',
            '<h3>1棟1日1組の、完全貸切</h3>\n        <p>10時から18時まで、1日1組だけ。清掃と準備の時間を確保しつつ、ムダのない運営で価格を抑えています。</p>')
    s = rep(s, '<p class="recommend__note-main">何人で来ても<br class="sp">1人 <em>16,500</em>円</p>', '<p class="recommend__note-main">何人で来ても<br class="sp">1人 <em>20,000</em>円</p>')
    s = rep(s, '<p class="sec__body">4時間貸切・施設利用・全機器の利用込み。<br>料金はお1人様あたりです。</p>', '<p class="sec__body">8時間貸切・施設利用・全機器・駅からの送迎込み。<br>料金はお1人様あたりです。</p>')
    s = rep(s, '<p class="price-flat__label">平日・土日、時間帯を問わず</p>', '<p class="price-flat__label">土日祝(平日は18,000円)</p>')
    s = rep(s, '<p class="price-flat__main">1人 <em>16,500</em><span>円</span></p>', '<p class="price-flat__main">1人 <em>20,000</em><span>円</span></p>')
    s = rep(s, '<p class="price-flat__note">一律料金。追加のオプション費用はありません。</p>', '<p class="price-flat__note">送迎・BBQ器材まで込み。BBQ食材セット(2,500円/人)などのオプションは任意です。</p>')
    s = rep(s, '      <li>外気浴・リラックス</li>\n    </ul>', '      <li>外気浴・リラックス</li>\n      <li>焚火ラウンジ・BBQ器材</li>\n      <li>駅からの送迎</li>\n    </ul>')
    s = rep(s, '<p class="pricing__member">回数も順番も自由。<br>4時間、何度でもお使いいただけます。</p>', '<p class="pricing__member">回数も順番も自由。<br>8時間、何度でもお使いいただけます。</p>')
    s = rep(s, '<p>はい。4時間の貸切時間内であれば、回数も順番も自由です。', '<p>はい。8時間の貸切時間内であれば、回数も順番も自由です。')
    s = rep(s, '<summary>1人でも利用できる?</summary>\n      <p>はい。貸切なので、周りを気にせず過ごせます。</p>',
            '<summary>何名から利用できる?</summary>\n      <p>2名からご予約いただけます。最大6名まで。貸切なので、周りを気にせず過ごせます。</p>')
    s = rep(s, '料金は何名でもお1人様16,500円で一律です。', '料金はお1人様20,000円(平日18,000円)です。')
    s = rep(s, '<p class="closing__body">10-14時と16-20時、1棟1日2組だけの2部制。<br>週末の枠から埋まっていきます。</p>', '<p class="closing__body">10時から18時まで、1棟1日1組だけ。<br>週末の日程から埋まっていきます。</p>')
    s = rep(s, '<span class="stickybar__label">4時間ぜんぶ込み</span>1人<em>16,500</em>円', '<span class="stickybar__label">8時間ぜんぶ込み</span>1人<em>20,000</em>円')
    s = re.sub(r'<meta name="description" content="[^"]*">',
               '<meta name="description" content="美容マシン3台・薪サウナ・水風呂・露天風呂・焚火BBQ、駅からの送迎まで、8時間ぜんぶ込みで1人20,000円(平日18,000円)。那須塩原・つくばの一棟を、10時から18時まで貸切。">', s, count=1)
    s = s.replace('<!-- Sec.6 証拠③: 空間と4時間の過ごし方 -->', '<!-- Sec.6 証拠③: 空間と1日の過ごし方 -->')
    return s

MACHINES_MORE = '''    <div class="machines__more">
      <h3>ほかにも、8種類。</h3>
      <p>店舗によって導入マシンが異なります。<strong>【マシン名は確認中。一覧が届き次第ここに入れます】</strong></p>
      <ul class="mc__parts">
        <li>【マシン名】</li><li>【マシン名】</li><li>【マシン名】</li><li>【マシン名】</li>
        <li>【マシン名】</li><li>【マシン名】</li><li>【マシン名】</li><li>【マシン名】</li>
      </ul>
    </div>
    <p class="machines__closing">※導入マシンは店舗により異なります。</p>'''

def apply_machines(s):
    s = rep(s, '<h2 class="sec__title">痩身エステも、小顔ケアも。<br>この3台を、好きなだけ。</h2>', '<h2 class="sec__title">11種類のマシンを、<br>好きなだけ。</h2>')
    s = rep(s, '<p class="sec__body">OHAKOは完全セルフ型。<br>使い方は当日ご案内します。回数も順番も自由です。</p>',
            '<p class="sec__body">OHAKOは完全セルフ型。<br>使い方は当日ご案内します。回数も順番も自由です。<br>まずは代表的な3台をご紹介します。</p>')
    s = rep(s, '    <p class="machines__closing">※導入マシンは店舗により異なります。</p>', MACHINES_MORE)
    s = rep(s, '<h3><span>価値 02</span>美容機器が、使い放題</h3>', '<h3><span>価値 02</span>美容マシン11種類が、使い放題</h3>')
    return s

# ------------------------------------------------------------------ 3大マシン(風・森・大地)訴求・那須塩原版
BIG3_MACHINES = '''    <article class="mc">
      <div class="mc__photo"><img src="img/kaze-face.jpg" alt="風 KAZE のRFフェイスケア" loading="lazy" width="715" height="573"></div>
      <div class="mc__body">
        <p class="mc__tag">MACHINE 01</p>
        <h3 class="mc__name">風 <small>KAZE</small></h3>
        <p class="mc__sub">RFでフェイス・ボディ</p>
        <p class="mc__catch">RFのやさしい温かさで、ハリのある肌へ。</p>
        <p class="mc__desc">電気エネルギーで肌をじんわり温める、<strong>RF(ラジオ波)美容ケア</strong>。頬はFチップ、フェイスラインや二の腕はVチップと、部位に合わせて使い分けます。</p>
        <div class="mc__result">
          <p class="mc__result-ttl">目指す印象</p>
          <ul>
            <li>顔のハリ不足、輪郭まわりのゆるみが気になる方へ。<strong>ふっくらすっきりした印象を目指します</strong></li>
            <li>温かさは「心地よい」が目安。<strong>熱く感じたらすぐにお伝えください</strong></li>
          </ul>
        </div>
        <ul class="mc__parts"><li>頬</li><li>フェイスライン</li><li>二の腕</li></ul>
      </div>
    </article>

    <article class="mc">
      <div class="mc__photo mc__photo--mori"><img src="img/mori-scene.jpg" alt="森 MORI 本体" loading="lazy" width="481" height="1044"></div>
      <div class="mc__body">
        <p class="mc__tag">MACHINE 02</p>
        <h3 class="mc__name">森 <small>MORI</small></h3>
        <p class="mc__sub">7ヘッドのボディケア</p>
        <p class="mc__catch">7つのヘッドから、今日の一本を。</p>
        <p class="mc__desc">二の腕・お腹・太ももまで。形も働きも違う7ヘッドで、ボディをケア。<strong>日本で人気の3大マシン(オンダリフト・インディバナイフ・ハイフキャビテーション)</strong>がぜんぶ使えます。</p>
        <div class="mc__result">
          <p class="mc__result-ttl">7つのヘッド</p>
          <ul>
            <li><strong>オンダリフト 浅層用・深層用</strong>｜冷却と熱を組み合わせたヘッド。浅層用は二の腕、深層用はお腹・太ももへ</li>
            <li><strong>インディバナイフ</strong>｜幅のある縁のナイフ型。温めながらやさしく触れる</li>
            <li><strong>ハイフキャビテーション</strong>｜丸い2本組のヘッドで、温熱などの刺激を楽しむ</li>
            <li><strong>EMSキャビテーション／ツボ押しRF／吸引RF</strong>｜ブラシ型・スティック型・カップ型の触れ心地</li>
          </ul>
        </div>
        <ul class="mc__parts"><li>二の腕</li><li>お腹</li><li>太もも</li><li>肩・背中</li></ul>
      </div>
    </article>

    <article class="mc">
      <div class="mc__photo"><img src="img/daichi-seat.jpg" alt="大地 DAICHI の専用シート" loading="lazy" width="719" height="573"></div>
      <div class="mc__body">
        <p class="mc__tag">MACHINE 03</p>
        <h3 class="mc__name">大地 <small>DAICHI</small></h3>
        <p class="mc__sub">座って骨盤底筋ケア</p>
        <p class="mc__catch">座ってケア。パルス × 「ぎゅっ」で、骨盤底筋へ。</p>
        <p class="mc__desc">服を着たまま専用シートに座ると、<strong>磁気のパルスが骨盤底筋に届きます</strong>。そのリズムに合わせて、ご自身でも「ぎゅっ」と締める意識を。機械の刺激と自分の力、ダブルで筋肉を使う感覚をねらえます。</p>
        <div class="mc__result">
          <p class="mc__result-ttl">使い方は3ステップ</p>
          <ul>
            <li>パルスで筋肉が動く → <strong>合わせてぎゅっと締める</strong> → ふっとゆるめる</li>
            <li>着替え不要。<strong>普段意識しにくい骨盤底筋へ</strong></li>
          </ul>
        </div>
        <ul class="mc__parts"><li>骨盤底筋</li><li>からだの土台</li><li>着替え不要</li></ul>
        <p class="mc__spec">※症状の改善を保証するものではありません。ペースメーカー等の植込み機器・体内金属がある方、妊娠中の方などは、ご利用前にスタッフへお伝えください。</p>
      </div>
    </article>

'''

def apply_big3(s):
    s = rep(s, '<title>OHAKO|痩身も小顔もサウナも、4時間ぜんぶ込みで16,500円（那須塩原・つくば・成田）</title>',
            '<title>OHAKO 那須塩原|最高級の3大マシンで過ごす、貸切セルフエステ。4時間ぜんぶ込みで1人16,500円</title>')
    s = re.sub(r'<meta name="description" content="[^"]*">',
               '<meta name="description" content="風・森・大地の3台・11種類。日本で人気の3大マシン(オンダリフト・インディバナイフ・ハイフキャビテーション)を含むセルフエステを、約30坪まるごと貸切の4時間で、自分のペースで。薪サウナ・水風呂・露天風呂・焚火ラウンジも込みで1人16,500円。OHAKO 那須塩原。">', s, count=1)
    # Sec.2 共感: 相場の金額は入れない
    s = re.sub(r'    <p class="empathy__price">.*?</p>\n    <p class="empathy__voice">.*?</p>\n    <p class="empathy__body">.*?</p>',
               '    <p class="empathy__voice">「いいマシンほど、<br class="sp">手が届かない」</p>\n    <p class="empathy__body">OHAKOなら、日本で人気の3大マシンを含む<br>全3台・11種類を、貸切で心ゆくまで。</p>', s, count=1, flags=re.S)
    # Sec.3 OHAKOとは
    s = rep(s, '<h2 class="sec__title">痩身エステも小顔ケアも、<br>自分のペースで。</h2>', '<h2 class="sec__title">最高級のマシンを、<br>自分のペースで。</h2>')
    s = rep(s, '<h3><span>価値 02</span>美容機器が、使い放題</h3>', '<h3><span>価値 02</span>美容マシン3台・11種類が、使い放題</h3>')
    s = rep(s, '          <li>痩身エステ(オンダリフト)</li>\n          <li>小顔ケア(表情筋パルス)</li>\n          <li>ボディメイク(筋肉パルス)</li>',
            '          <li>風 KAZE(RFでフェイス・ボディ)</li>\n          <li>森 MORI(7ヘッドのボディケア)</li>\n          <li>大地 DAICHI(座って骨盤底筋ケア)</li>')
    # Sec.4 相場比較は入れない(景表法配慮)
    s = re.sub(r'<!-- Sec\.4 証拠①: 相場比較 -->.*?</section>\n\n', '', s, count=1, flags=re.S)
    # Sec.5 導入機器を風・森・大地に
    s = rep(s, '<h2 class="sec__title">痩身エステも、小顔ケアも。<br>この3台を、好きなだけ。</h2>', '<h2 class="sec__title">風・森・大地。<br>3台・11種類を、好きなだけ。</h2>')
    s = rep(s, '<p class="sec__body">OHAKOは完全セルフ型。<br>使い方は当日ご案内します。回数も順番も自由です。</p>',
            '<p class="sec__body">OHAKOは完全セルフ型。<br>使用部位・当て方・設定は当日スタッフがご案内します。回数も順番も自由です。</p>')
    i = s.index('    <article class="mc">'); j = s.index('    <p class="machines__closing">')
    s = s[:i] + BIG3_MACHINES + s[j:]
    s = rep(s, '<p class="machines__closing">※導入マシンは店舗により異なります。</p>',
            '<p class="machines__closing">※ケアの目的は目指す印象を示すもので、効果や結果を保証するものではありません。感じ方には個人差があります。</p>')
    # Sec.5.5 流れ
    s = rep(s, '<span class="cycle__how">筋肉パルス・表情筋パルス</span>', '<span class="cycle__how">大地(骨盤底筋)・風(RF)</span>')
    s = rep(s, '<span class="cycle__how">オンダリフト</span>', '<span class="cycle__how">森(7ヘッドのボディケア)</span>')
    s = rep(s, '<p class="get__desc">痩身エステでボディを、小顔ケアでフェイスラインを。気になっていたラインが、すっきりとした印象へ。</p>',
            '<p class="get__desc">森でボディを、風でフェイスラインを。気になっていたラインが、すっきりとした印象を目指せます。</p>')
    # Sec.9 料金に含まれるもの
    s = rep(s, '      <li>筋肉パルス</li>\n      <li>表情筋パルス</li>\n      <li>オンダリフト</li>', '      <li>風(RF)</li>\n      <li>森(7ヘッド)</li>\n      <li>大地(骨盤底筋)</li>')
    return s

def only_nasu(s):
    """施設一覧を那須塩原だけにする(予約リンク付与後に呼ぶ)"""
    s = rep(s, '<h2 class="sec__title">施設一覧</h2>', '<h2 class="sec__title">アクセス</h2>')
    s = re.sub(r'      <li class="shop">\n        <div class="shop__map">\n          <iframe\n            src="[^"]*"\n            title="OHAKO (つくば|成田)の地図".*?      </li>\n', '', s, flags=re.S)
    assert 'OHAKO つくば' not in s and 'OHAKO 成田' not in s, 'shop removal failed'
    s = rep(s, '<p class="shop__note">ご予約時に、ご希望の施設をお選びいただけます。</p>',
            '<p class="shop__note">那須塩原駅(東北新幹線)から。東京駅から新幹線で約70分。お車の方は施設の駐車場(無料)をご利用ください。</p>')
    return s

# ------------------------------------------------------------------ 予約ページ導線
def apply_book(s, plan):
    url = BOOK_8H if plan == '8h' else BOOK_4H
    s = s.replace(LINE_URL, url)
    s = s.replace('class="btn-line js-line"', 'class="btn-line btn-book js-book"').replace('class="btn-line btn-line--lg js-line"', 'class="btn-line btn-line--lg btn-book js-book"').replace('class="stickybar__btn js-line"', 'class="stickybar__btn stickybar__btn--book js-book"')
    s = s.replace('>LINEで空き状況を見る</a>', '>空き日程を見て予約する</a>').replace('>LINEで予約</a>', '>空きを見て予約</a>')
    s = s.replace('登録30秒|予約はLINE限定', '日付と人数を選んでカード決済|予約はオンラインで完結')
    s = rep(s, '<p class="closing__lead">予約はLINEだけ。<br>30秒ではじめられます。</p>', '<p class="closing__lead">予約はオンラインで完結。<br>空き日程をその場で確認できます。</p>')
    s = rep(s, '<p class="cta__note cta__note--light">しつこい通知は送りません</p>', '<p class="cta__note cta__note--light">決済完了で予約確定。前日にLINEで当日のご案内をお送りします。</p>')
    s = rep(s, '<h3>LINEで友だち登録</h3>\n        <p>30秒で完了。</p>', '<h3>空き日程を選ぶ</h3>\n        <p>カレンダーで○の日を選ぶだけ。</p>')
    s = rep(s, '<h3>日時とメニューを選ぶ</h3>\n        <p>空き状況もLINEで見られます。</p>', '<h3>人数を選んで、決済</h3>\n        <p>料金はその場で表示。カード決済で確定。</p>')
    for name, link in BOOK_FAC[plan].items():
        anchor = '<h3 class="shop__name">%s</h3>' % name
        s = rep(s, anchor, anchor + '\n          <a class="shop__book" href="%s">この施設を予約する</a>' % link)
    return s

# ------------------------------------------------------------------ 生成
CTA_LINE = ('    <div class="cta">\n      <a class="btn-line js-line" href="%s">LINEで空き状況を見る</a>\n      <p class="cta__note">登録30秒|予約はLINE限定</p>\n    </div>\n' % LINE_URL)

EXTRA_CSS = '''
/* variants */
.btn-book, .btn-book:hover { background: linear-gradient(135deg, #d4b070 0%, #a87f3f 100%) !important; color: #fff; }
.stickybar__btn--book { background: linear-gradient(135deg, #d4b070 0%, #a87f3f 100%) !important; color: #fff !important; }
.shop__book { display: inline-block; margin: 8px 0 0; padding: 8px 14px; border-radius: 999px; background: #c19a5b; color: #fff; font-size: 12.5px; font-weight: 700; }
.machines__more { margin-top: 28px; background: rgba(193,154,91,.08); border: 1px dashed #c19a5b; border-radius: 14px; padding: 18px; }
.machines__more h3 { margin: 0 0 8px; font-size: 18px; }
.machines__more p { margin: 0 0 10px; font-size: 13.5px; color: #6d6458; }
.mc__name small { font-size: 12px; letter-spacing: .3em; color: #a87f3f; margin-left: 8px; font-family: "Noto Serif JP", serif; }
.mc__photo--mori img { object-position: center 35%; }
'''

os.makedirs(os.path.join(ROOT, 'css'), exist_ok=True)
css = open(os.path.join(ROOT, 'base', 'css', 'style.css'), encoding='utf-8').read()
open(os.path.join(ROOT, 'css', 'style.css'), 'w', encoding='utf-8').write(css + EXTRA_CSS)
if os.path.isdir(os.path.join(ROOT, 'img')): shutil.rmtree(os.path.join(ROOT, 'img'))
shutil.copytree(os.path.join(ROOT, 'base', 'img'), os.path.join(ROOT, 'img'))
for f in ('legal.html', 'privacy.html'):
    shutil.copy(os.path.join(ROOT, 'base', f), os.path.join(ROOT, f))

rows = []
for v in VARIANTS:
    s = BASE
    if v['plan'] == '8h':
        s = apply_8h(s)
    if v['appeal'] == 'machines':
        s = apply_machines(s)
    if v['appeal'] == 'big3':
        s = apply_big3(s)
    blk = fv_block(v['appeal'], v['plan'], CTA_LINE)
    if blk:
        i = s.index(FV_START); j = s.index(FV_END_MARK); j = s.index('</p>', j) + len('</p>\n')
        s = s[:i] + blk + s[j:]
    if v['cta'] == 'book':
        s = apply_book(s, v['plan'])
    if v['appeal'] == 'big3':
        s = only_nasu(s)
    # 共有アセットへの相対パス
    s = s.replace('href="css/', 'href="../css/').replace('src="img/', 'src="../img/').replace('href="privacy.html"', 'href="../privacy.html"').replace('href="legal.html"', 'href="../legal.html"')
    # 識別用コメント
    s = s.replace('<head>', '<head>\n<!-- variant: %s | %s | %s | %s | %s -->' % (v['slug'], v['label'], v['cta_label'], v['plan_label'], v['price_label']), 1)
    out = os.path.join(ROOT, v['slug'])
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(s)
    rows.append(v)
    print('built', v['slug'])

table = '\n'.join('      <tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><a href="%s/">開く</a></td></tr>' % (
    html.escape(v['label']), v['cta_label'], v['plan_label'], v['price_label'], v['slug']) for v in rows)
index = '''<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OHAKO LP 訴求×導線テスト 一覧</title><meta name="robots" content="noindex, nofollow">
<style>body{font-family:system-ui,sans-serif;background:#f6f1e8;color:#241f18;margin:0;padding:24px}h1{font-size:20px}table{border-collapse:collapse;background:#fff;width:100%%;max-width:900px}th,td{border:1px solid #e6dfd3;padding:10px 12px;text-align:left;font-size:14px}th{background:#16130e;color:#c19a5b}a{color:#a87f3f;font-weight:700}p{font-size:13px;color:#6d6458}</style></head>
<body><h1>OHAKO LP 訴求 × 導線 テスト一覧</h1>
<p>ベース: 既存LP(ohako-self-lp)。FV・CTA・時間/料金の文言だけを差し替えた派生版。予約ページ版のリンク先は本番の予約ページです。</p>
<table><thead><tr><th>訴求</th><th>導線</th><th>枠の使い方</th><th>料金</th><th></th></tr></thead><tbody>
%s
</tbody></table>
<p>LINE版の登録リンクは現在すべて共通(uLand=hKe9eZ)。訴求ごとに流入経路を分ける場合は build.py の LINE_URL を変更して再生成。</p>
</body></html>
''' % table
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(index)
print('built index.html')
