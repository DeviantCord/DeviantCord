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

import org.javacord.api.entity.permission.Role;
import org.javacord.api.entity.server.Server;
import org.javacord.api.entity.user.User;

import java.util.List;

public class L1CheckObject {

    private User interactedUser;
    private Server obtServer;
    private List<Role> userRoles;
    private long serverId;
    private String serverIdStr;
    private long convertRole;
    private boolean failedCheck;
    private String failureReason;

    public void setInteractedUser(User givenUser){interactedUser = givenUser;}
    public User getInteractedUser(){return interactedUser;}
    public void setObtServer(Server givenServer){obtServer = givenServer;}
    public Server getObtServer(){return obtServer;}
    public void setUserRoles(List<Role> givenRoles){userRoles = givenRoles;}
    public List<Role> getUserRoles(){return userRoles;}
    public void setServerId(long givenId){serverId = givenId;}
    public long getServerId(){return serverId;}

    public void setServerIdStr(String serverIdStr) {
        this.serverIdStr = serverIdStr;
    }

    public void setConvertRole(long convertRole) {
        this.convertRole = convertRole;
    }

    public void setFailedCheck(boolean failedCheck) {
        this.failedCheck = failedCheck;
    }

    public void setFailureReason(String failureReason) {
        this.failureReason = failureReason;
    }

    public boolean isFailedCheck() {
        return failedCheck;
    }

    public long getConvertRole() {
        return convertRole;
    }

    public String getFailureReason() {
        return failureReason;
    }

    public String getServerIdStr() {
        return serverIdStr;
    }
}
