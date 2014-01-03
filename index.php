<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>HostMonitoring</title>
    </head>
    <body>
        <?php
            $graph = '/srv/www/lighttpd/hostmon/graph/';
            $host  = '';
            if ( isset($_GET['host']) ) {
                $host = $_GET['host'];
                $graph = $graph . $host;
                if (is_dir($graph)) {
                    if ($dh = opendir($graph)) {
                        $list = array();
                        while (false !== ($file = readdir($dh))) {
                            if ($file != "." && $file != "..") {
                                $list[] = $file;
                            }
                        }
                        rsort($list);
                        foreach ( $list as $file ) {
                            $png = 'graph/' . $host . '/' . $file;
                            ?>
                                <img src="<?= $png?>" border="0" alt="<?= $file?>" title="<?= $file?>"/>
                                <br>
                            <?
                        }
                    }
                }
            } else {
                if (is_dir($graph)) {
                    if ($dh = opendir($graph)) {
                        while (false !== ($file = readdir($dh))) {
                            if ($file != "." && $file != "..") {
                                $png = 'graph/' . $file . '/' . date('Ymd.p\n\g');
                                ?>
                                    <a href="?host=<?= $file?>"><img src="<?= $png?>" border="0"/></a>
                                <?
                            }
                        }
                    }
                }
            }
        ?>
    </body>
</html>
