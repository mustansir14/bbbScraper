<?php
namespace DataExport\Helpers;

class Db
{
    private string $sql;
    private string $error;

    public function __construct()
    {
        $this->db = null;
        $this->sql = "";
        $this->error = "";
    }

    public function connect( string $host, string $user, string $pass, string $db )
    {
        $this->db = new \Mysqli( $host, $user, $pass, $db );
        if ($this->db->connect_errno) {
            $this->error = $this->db->connect_error;
            return false;
        }

        $this->db->set_charset('utf8mb4');

        return true;
    }

    public function connectOrDie( string $host, string $user, string $pass, string $db )
    {
        if ( !$this->connect( $host, $user, $pass, $db ) )
        {
            die( $this->error() );
        }
    }

    protected function getSQLParamValue( $value )
    {
        if ( $value === null || $value === false || ( is_string( $value ) && strlen( $value ) == 0 ) )
        {
            return "NULL";
        }

        if ( is_int( $value ) )
        {
            return sprintf( "%d", $value );
        }

        if( is_array( $value ) )
        {
            return $value[0]; # raw sql
        }

        return "'".$this->db->real_escape_string( $value )."'";
    }

    public function escape( $value )
    {
        return $this->db->real_escape_string( $value );
    }

    protected function fieldsToString( $fields )
    {
        if ( !is_array( $fields ) )
        {
            # will be error on execution
            return "";
        }

        $sql = "";
        $tab = str_repeat( " ", 4 );

        $counter = 0;
        foreach( $fields as $fieldName => $fieldValue )
        {
            $sql .= ( $counter ? ",\n{$tab}" : "" ). $fieldName." = ".$this->getSQLParamValue( $fieldValue );
            $counter++;
        }

        return $sql;
    }

    protected function buildSQLQuery( $options )
    {
        $sql = "";
        $tab = str_repeat( " ", 4 );

        #var_dump( $options );

        $options["type"] = strtolower( $options["type"] );

        if ( !is_array( $options['tables'] ) )
            $options['tables'] = [ $options['tables'] ];

        if ( $options["type"] == "select" )
        {
            $options['fields'] = is_array( $options['fields'] ) ? implode( ",\n{$tab}", $options['fields'] ) : $options['fields'];

            if ( $options["tables"][0] instanceof MysqlUnion )
            {
                $sql .= "SELECT \n{$tab}{$options['fields']} \nFROM ( ".$options["tables"][0]->getSQL()." ) ".$options["tables"][0]->getAlias();
            }else{
                $sql .= "SELECT \n{$tab}{$options['fields']} \nFROM {$options['tables'][0]}";
            }
        }elseif ( $options["type"] == "delete" )
        {
            $sql .= "DELETE FROM \n{$tab}{$options['tables'][0]}";
        }elseif( $options["type"] == "insert" )
        {
            $sql .= "INSERT INTO \n{$tab}{$options['tables'][0]} \nSET \n{$tab}".$this->fieldsToString( $options["fields"] ).
                ( isset( $options["onDuplicateKeyUpdate"] ) && $options["onDuplicateKeyUpdate"] ? " \nON DUPLICATE KEY UPDATE \n".$this->fieldsToString( $options['onDuplicateKeyUpdate'] ) : "" );
        }elseif( $options["type"] == "update" )
        {
            $sql .= "UPDATE \n{$tab}{$options['tables'][0]} \nSET \n{$tab}".$this->fieldsToString( $options["fields"] );
        }else{
            return false;
        }

        foreach( $options["tables"] as $k => $v )
        {
            if ( $k == "0" ) continue;

            $sql .= " \nLEFT JOIN {$k} ON {$v}";
        }

        if ( isset( $options["where"] ) && $options["where"] )
        {
            $sql .= " \nWHERE \n{$tab}";

            if ( is_array( $options["where"] ) )
            {
                if ( isset( $options["where"][0] ) )
                {
                    $sql .= implode( " AND \n{$tab}", $options["where"] );
                }else{
                    $counter = 0;
                    foreach( $options["where"] as $k => $v )
                    {
                        $sql .= ( $counter ? " AND \n{$tab}" : "" ).$k." = ".$this->getSQLParamValue( $v );
                        $counter++;
                    }
                }
            }else{
                $sql .= $options["where"];
            }
        }

        if ( isset( $options["group"] ) && $options["group"] )
        {
            $sql .= " \nGROUP BY ".$options["group"];
        }

        if ( isset( $options["order"] ) && $options["order"] )
        {
            $sql .= " \nORDER BY ".$options["order"];
        }

        if ( isset( $options["limit"] ) && $options["limit"] )
        {
            $sql .= " \nLIMIT ".( is_array( $options["limit"] ) ? $options["limit"][0].",".$options["limit"][1] : $options['limit'] );
        }

        #echo $sql;

        return $sql;
    }

    public function query( $sql )
    {
        $this->sql = $sql;
        $this->error = "";

        #echo $sql."\n";

        $rs = $this->db->query( $sql );
        if ( !$rs )
        {
            $this->error = $this->db->error;
            return false;
        }

        return $rs;
    }

    public function queryColumn( $sql, $columnName )
    {
        $rows = $this->queryArray( $sql );
        if ( !$rows ) return $rows;

        return array_map( function ( $row ) use ( $columnName ) {
            return $row[ $columnName ];
            }, $rows );
    }

    public function queryArray( $sql )
    {
        $rs = $this->query( $sql );
        if ( $rs === false ) return false;

        $rows = [];
        while ( $r = $rs->fetch_assoc() )
        {
            $rows[] = $r;
        }

        return $rows;
    }

    public function queryRow( $sql )
    {
        $rows = $this->queryArray( $sql );
        if ( $rows === false ) return false;

        return $rows[0] ?? null;
    }

    public function countRows( $tables, $where = false, $limit = false )
    {
        $sql = $this->buildSQLQuery( [
            "type" => "select", "fields" => "count(*) cnt", "tables" => $tables, "where" => $where, "limit" => $limit,
        ] );

        $row = $this->queryRow( $sql );
        if ( !$row ) return $row;

        return $row[ "cnt" ];
    }

    public function insert( $tables, $fields, $onDuplicateKeyUpdate = false )
    {
        $sql = $this->buildSQLQuery( [
            "type"                 => "insert", "fields" => $fields, "tables" => $tables,
            "onDuplicateKeyUpdate" => $onDuplicateKeyUpdate,
        ] );

        $rs = $this->query( $sql );
        return (bool)$rs;
    }

    public function insertID(): int
    {
        return $this->db->insert_id;
    }

    public function selectArray( $fields, $tables, $where = false, $group = false, $order = false, $limit = false )
    {
        $sql = $this->buildSQLQuery([
            "type" 	 => "select",
            "fields" => $fields,
            "tables" => $tables,
            "where"  => $where,
            "group"  => $group,
            "order"  => $order,
            "limit"  => $limit,
        ]);

        return $this->queryArray( $sql );
    }

    public function selectRow( $fields, $tables, $where = false, $group = false, $order = false, $limit = false )
    {
        $rows = $this->selectArray( $fields, $tables, $where, $group, $order, $limit );
        if ( $rows === false ) return false;

        return $rows[0] ?? null;
    }

    public function selectColumn( $columnName, $tables, $where = false, $group = false, $order = false, $limit = false )
    {
        $row = $this->selectRow( $columnName, $tables, $where, $group, $order, $limit );
        if ( $row === false ) return false;

        return $row ? reset( $row ) : null;
    }

    public function delete( $tables, $where )
    {
        $sql = $this->buildSQLQuery([
            "type" 	 => "delete",
            "tables" => $tables,
            "where"  => $where,
        ]);

        return (bool)$this->query( $sql );
    }

    public function update( $tables, $fields, $where )
    {
        $sql = $this->buildSQLQuery([
            "type" 	 => "update",
            "fields" => $fields,
            "tables" => $tables,
            "where"  => $where,
        ]);

        return (bool)$this->query( $sql );
    }

    public function getExtendedError()
    {
        return $this->error ? $this->getSQL()."\n".$this->getError() : "";
    }

    public function getError()
    {
        return $this->error;
    }

    public function getSQL()
    {
        return $this->sql;
    }
}