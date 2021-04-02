<?php

$importer = new Importer();
$data = json_decode(file_get_contents('./data.json'), 1);
foreach ($data as $date => $row) {
    echo $date . "\n";
    $importer->processRow($date, $row);
}


class Importer {

    protected $pdo;
    protected $columnsByIndex = [];
    protected $columnsByTitle = [];

    public function __construct() {
        $this->pdo = new PDO('mysql:host=localhost;dbname=coronahh', 'import', '');
        $this->loadColumns();
    }

    public function loadColumns() {
        $this->columnsById = [];
        $this->columnsByTitle = [];
        $sql = "SELECT * FROM columns";
        foreach ($this->pdo->query($sql) as $row) {
            $this->columnsById[$row['id']] = $row['title'];
            $this->columnsByTitle[$row['title']] = $row['id'];
        }
    }

    public function processRow($date, $row, $prefix = '') {

        foreach ($row as $k => $v) {
            if (is_array($v)) {
                $this->processRow($date, $v, $prefix . '-' . $k);
            } else {
                $colTitle = $prefix . '-' . $k;
                if (!isset($this->columnsByTitle[$colTitle])) {
                    $id = $this->addColumn($colTitle);
                    $this->columnsByTitle[$colTitle] = $id;
                    $this->columnsByIndex[$id] = $colTitle;
                }
                $colIndex = $this->columnsByTitle[$colTitle];
                $this->insertUpdate($date, $colIndex, $v);
            }
        }
    }

    public function insertUpdate($date, $colIndex, $value) {

        $d = substr($date, 0, 4)
            . '-' . substr($date, 4, 2)
            . '-' . substr($date, 6, 2);

        $this->pdo->prepare('INSERT INTO data (date, id_column, value) VALUES (:date, :colIndex, :value) ON DUPLICATE KEY UPDATE value=:value')
            ->execute(['date' => $d, 'colIndex' => $colIndex, 'value' => $value]);
    }

    public function addColumn($title) {
        $this->pdo->prepare('INSERT INTO columns (title) VALUES (:title)')
            ->execute(['title' => $title]);
        return $this->pdo->lastInsertId();
    }
}
