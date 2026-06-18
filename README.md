# kaji-kiroku-app
1. ユースケース図
flowchart LR
    User((ユーザ))
    
    User --> UC1[家事を登録する]
    User --> UC2[経過日数順で家事一覧を見る]
    User --> UC3[「今日やった」ボタンを押す]
    User --> UC4[不要になった家事を削除する]
2. クラス図
classDiagram
    class Chore {
        -String id
        -String name
        -Date lastCompletedDate
        +create()
        +readAllSortedByDays()
        +updateDateToToday()
        +delete()
    }
3.シーケンス図
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
    End
4. 状態遷移図
stateDiagram-v2
    %% 初期状態
    [*] --> 未実施 : 家事を新規登録する

    %% 状態と遷移
    未実施 --> 実施済み : 「今日やった」ボタンを押下する
    
    %% 自己遷移（状態は変わらず内部データが更新される）
    実施済み --> 実施済み : 再度「今日やった」ボタンを押下する\n(最終実施日が最新に更新される)

    %% 終了状態への遷移（削除）
    未実施 --> 削除済み : 削除操作を行う
    実施済み --> 削除済み : 削除操作を行う
    
    %% 終了状態
    削除済み --> [*]
