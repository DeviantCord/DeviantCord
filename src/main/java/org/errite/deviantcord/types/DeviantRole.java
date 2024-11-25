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
package org.errite.deviantcord.types;

import java.sql.Timestamp;

public class DeviantRole {
    public static long RoleId;
    public static Timestamp assigned;
    public DeviantRole(long given_role, Timestamp assigned_timestamp)
    {
        RoleId = given_role;
        assigned = assigned_timestamp;
    }
    public DeviantRole()
    {

    }

    public void setRoleId(long input){RoleId = input;}
    public void setAssigned(Timestamp input){assigned = input;}
    public long getDeviantRoleId(){return RoleId;}
    public Timestamp getAssigned(){return assigned;}

}
