begin
  do_something();
  -- framework-exclude-begin: PMD does not like dbms_lob.trim (clash with TrimExpression)
  dbms_lob.trim(the_blob, 1000);
  -- framework-exclude-end
  do_something_else(x);
end;
/

select dummy from dual a
where 1=1
  -- framework-exclude-begin: PMD does not like scalar subqueries in WHERE conditions
  and 'J' = (select max('J') from dual b)
  -- framework-exclude-end
;
