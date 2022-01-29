#!/bin/bash
psql -U postgres -d ramendb -A -F, -t << EOF
    select l.longitude, l.latitude from shops_location as l join shops as s on l.sid = s.sid
    where s.pref = '新潟県' and s.area like '新潟市%' and l.longitude != 0 and l.latitude !=0;
EOF
exit $?