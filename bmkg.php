<?php
// Get API URL
$api_url = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=31.71.01.1001";
$response_body = @file_get_contents($api_url);

// Check if fail
if ($response_body === false) {
    die("ERROR: Gagal mengambil data.");
}

// Decode String JSON
$data = json_decode($response_body, true);

if ($data === null && json_last_error() !== JSON_ERROR_NONE) {
    die(
        "ERROR: Data bukan format JSON yang valid. " .
            htmlspecialchars(json_last_error_msg())
    );
}

// Set header
header("Content-Type: text/html; charset=utf-8");
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prakiraan Cuaca BMKG</title>
    <style>
        body { font-family: sans-serif; line-height: 1.5; padding: 15px; }
        h2, h3, h4 { margin-top: 1.5em; margin-bottom: 0.5em; }
        ul { list-style: none; padding-left: 0; }
        li { margin-bottom: 0.5em; border-bottom: 1px solid #eee; padding-bottom: 0.5em; }
        img { width: 20px; height: 20px; vertical-align: middle; margin-left: 5px; }
        pre { background-color: #f4f4f4; padding: 10px; border: 1px solid #ddd; overflow-x: auto; }
    </style>
</head>
<body>

<h1>Prakiraan Cuaca BMKG</h1>

<?php
// Location
if (isset($data["lokasi"]["desa"]) && isset($data["lokasi"]["kecamatan"])) {
    echo "<h2>Desa/Kelurahan: " .
        htmlspecialchars($data["lokasi"]["desa"]) .
        "</h2>";
    echo "<p>";
    echo "Kecamatan: " .
        htmlspecialchars($data["lokasi"]["kecamatan"] ?? "N/A") .
        "<br>";
    echo "Kota/Kab: " .
        htmlspecialchars($data["lokasi"]["kotkab"] ?? "N/A") .
        "<br>";
    echo "Provinsi: " .
        htmlspecialchars($data["lokasi"]["provinsi"] ?? "N/A") .
        "<br>";
    echo "Koordinat: Lat: " .
        htmlspecialchars($data["lokasi"]["lat"] ?? "N/A") .
        ", Lon: " .
        htmlspecialchars($data["lokasi"]["lon"] ?? "N/A") .
        "<br>";
    echo "Timezone: " .
        htmlspecialchars($data["lokasi"]["timezone"] ?? "N/A") .
        "<br>";
    echo "</p>";
} else {
    echo "<h2>Lokasi Tidak Ditemukan</h2>";
}

// Weather forecast data
echo "<h3>Detail Prakiraan Cuaca:</h3>";
if (isset($data["data"][0]["cuaca"]) && is_array($data["data"][0]["cuaca"])) {
    foreach ($data["data"][0]["cuaca"] as $index_hari => $prakiraan_harian) {
        echo "<h4>Hari ke-" . ($index_hari + 1) . "</h4>";
        echo "<ul>";
        if (is_array($prakiraan_harian)) {
            foreach ($prakiraan_harian as $prakiraan) {
                $waktu_lokal = isset($prakiraan["local_datetime"])
                    ? htmlspecialchars($prakiraan["local_datetime"])
                    : "N/A";
                $deskripsi = isset($prakiraan["weather_desc"])
                    ? htmlspecialchars($prakiraan["weather_desc"])
                    : "N/A";
                $alt_text = isset($prakiraan["weather_desc"])
                    ? htmlspecialchars(
                        $prakiraan["weather_desc"],
                        ENT_QUOTES,
                        "UTF-8"
                    )
                    : "Ikon Cuaca";
                $suhu = isset($prakiraan["t"])
                    ? htmlspecialchars($prakiraan["t"])
                    : "N/A";
                $kelembapan = isset($prakiraan["hu"])
                    ? htmlspecialchars($prakiraan["hu"])
                    : "N/A";
                $kec_angin = isset($prakiraan["ws"])
                    ? htmlspecialchars($prakiraan["ws"])
                    : "N/A";
                $arah_angin = isset($prakiraan["wd"])
                    ? htmlspecialchars($prakiraan["wd"])
                    : "N/A";
                $jarak_pandang = isset($prakiraan["vs_text"])
                    ? htmlspecialchars($prakiraan["vs_text"])
                    : "N/A";

                $raw_img_url = isset($prakiraan["image"])
                    ? $prakiraan["image"]
                    : "";
                $img_url_processed = "";

                if (!empty($raw_img_url)) {
                    $img_url_processed = str_replace(" ", "%20", $raw_img_url);
                }

                echo "<li>";
                echo "<strong>Jam:</strong> " . $waktu_lokal . " | ";
                echo "<strong>Cuaca:</strong> " . $deskripsi . " ";
                if (
                    $img_url_processed &&
                    filter_var($img_url_processed, FILTER_VALIDATE_URL)
                ) {
                    echo '<img src="' .
                        $img_url_processed .
                        '" alt="' .
                        $alt_text .
                        '" title="' .
                        $alt_text .
                        '"> | ';
                }
                echo "<strong>Suhu:</strong> " . $suhu . "°C | ";
                echo "<strong>Kelembapan:</strong> " . $kelembapan . "% | ";
                echo "<strong>Kec. Angin:</strong> " . $kec_angin . "km/j | ";
                echo "<strong>Arah Angin:</strong> dari " . $arah_angin . " | ";
                echo "<strong>Jarak Pandang:</strong> dari " . $jarak_pandang;
                echo "</li>";
            }
        } else {
            echo "<li>Data tidak valid.</li>";
        }
        echo "</ul>";
    }
} else {
    echo "<p>Struktur data prakiraan cuaca tidak ditemukan.</p>";
}

// Debugging $data
/*
echo "<pre>";
print_r($data);
echo "</pre>";
*/
?>
</body>
</html>