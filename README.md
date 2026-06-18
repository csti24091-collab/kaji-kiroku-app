# kaji-kiroku-app
# 名もなき家事・掃除記録アプリ (Chore Tracker)

一人暮らしにおける「名もなき家事」や定期的な掃除の「最後にいつやったか」を記録し、次にやるべき家事を可視化するWebアプリケーションです。

## 設計図 (Architecture Diagrams)

### ユースケース図
```mermaid
flowchart LR
    User((ユーザ))
    
    User --> UC1[家事を登録する]
    User --> UC2[経過日数順で家事一覧を見る]
    User --> UC3[「今日やった」ボタンを押す]
    User --> UC4[不要になった家事を削除する]
```
### クラス図
```mermaid
classDiagram
    class 家事マネージャー {
        +リスト~家事~ 家事リスト
        +家事追加(名前: 文字列)
        +経過日数順の家事リスト取得() リスト~家事~
        +家事削除(ID: 文字列)
    }

    class 家事 {
        -文字列 id
        -文字列 名前
        -日付 最終完了日
        +日付を今日に更新する()
    }

    家事マネージャー "1" *-- "0..*" 家事 : 管理する
```
### シーケンス図
```mermaid
sequenceDiagram
    autonumber
    actor User as ユーザ
    participant UI as 画面(UI)
    participant Ctrl as コントローラ
    participant DB as モデル(DB)
 
    %% 家事一覧の取得と表示
    User->>UI: アプリにアクセス
    UI->>Ctrl: 一覧取得リクエスト
    Ctrl->>DB: 全家事データの取得
    DB-->>Ctrl: データ返却
    
    loop 取得した全データに対する処理
        Ctrl->>Ctrl: 最終実施日からの経過日数を計算
    end
    
    Ctrl->>Ctrl: 経過日数順(降順)に並び替え
    Ctrl-->>UI: 描画用データを渡す
    UI-->>User: 経過日数順の家事一覧を表示
 
    %% 「今日やった」ボタンの操作
    User->>UI: 「今日やった」ボタンを押下
    UI->>Ctrl: 更新リクエスト送信 (家事ID)
    
    alt 更新が成功した場合
        Ctrl->>DB: 対象データの最終実施日を「本日」に更新
        DB-->>Ctrl: 更新完了
        Ctrl-->>UI: 一覧画面の再読み込みを指示
        UI-->>User: 最新の家事一覧を表示
    else データが存在しないなどのエラー時
        Ctrl->>DB: 対象データの更新を試行
        DB-->>Ctrl: エラー返却
        Ctrl-->>UI: エラーメッセージを渡す
        UI-->>User: エラー（「更新できませんでした」等）を表示
    end
```
### 状態遷移図
```mermaid
stateDiagram-v2
    [*] --> 未実施 : 家事を新規登録する
 
    未実施 --> 実施済み : 「今日やった」ボタンを押下する
    
    実施済み --> 実施済み : 再度「今日やった」ボタンを押下する\n(最終実施日が最新に更新される)
 
    未実施 --> 削除済み : 削除操作を行う
    実施済み --> 削除済み : 削除操作を行う
```
    
    削除済み --> [*]
