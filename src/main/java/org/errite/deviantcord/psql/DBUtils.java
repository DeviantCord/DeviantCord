/*
 * DeviantCord 4
 * Copyright (C) 2020-2024  Errite Softworks LLC/ ErriteEpticRikez
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
package org.errite.deviantcord.psql;

import java.sql.ResultSet;
import java.sql.SQLException;

public class DBUtils {
    public static boolean resultSetEmpty(ResultSet given_rs) throws SQLException {
        int size =0;
        if(given_rs == null)
            //TODO If this is thrown during testing, then change this to just return true
            throw new NullPointerException("Null ResultSet");
        if (given_rs != null)
        {
            given_rs.last();    // moves cursor to the last row
            size = given_rs.getRow(); // get row id
        }
        if(size == 0)
        {
            given_rs.beforeFirst();
            return true;
        }
        else
        {
            given_rs.beforeFirst();
            return false;
        }
    }

    public static int getResultSetSize(ResultSet given_rs) throws SQLException {
        int rowCount = 0;
        while (given_rs.next()) {
            rowCount++;
        }
        // Reset cursor back to the beginning if needed
        given_rs.beforeFirst();
        return rowCount;

    }
}
